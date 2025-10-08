---
title: "Extracting IP and port from a meterpreter payload"
date: 2019-05-21 20:48:15
draft: false
categories: ['Deobfuscation', 'Forensics', 'Incident Response', 'Powershell']
tags: ['forensics', 'incident response', 'metaspolit', 'meterpreter', 'reverse shell', 'shellcode']
---

When an attacker has already gained access to our network and he managed to steal some passwords or hashes, he is usually looking to break into something more interesting than HR workstation. This is a time when he uses stolen passwords to gain access to servers crucial for his operations.

If you see a service installation event (7045) in your System log, with PowerShell code containing a gzipped payload, this is most likely evidence of the attacker's lateral movement.

![Evidence of lateral movement](/images/2019/05/meterpreter1.png)

<!--more-->

This is how it looks like from the attacker's perspective. Note that despite the 6 hours time difference (different timezone - something to always check for during your investigations), this is the same event.

![Attacker exploiting stolen credentials to gain access to a server](/images/2019/05/meterpreter2.png)

Unfortunately, the windows event doesn't tell us straight away who performed the attack. The user account that installed the service is the one that got compromised but we don't know by who. There are multiple ways to associate this event with the attacker. For example, you may want to try to correlate with User Logon type 3 from the Security log. This will tell you which IP was used to login on compromised credentials, which will be most likely an IP of the attacker.

![User logon on compromised credentials. Visible IP of the attacker.](/images/2019/05/logon.png)

However, if you don't have this information available immediately (let's say you received only this one event as an alert from monitoring) or you just want to confirm it, or you suspect that the attacker is using different IPs to login that to perform the rest of his actions, you may want to dive into the PowerShell code.

If you take a closer look this is a gzip-compressed payload, so we should decompress it for further investigation. It can be done by PowerShell of course, CyberChef, Linux command, python, and many other tools. After unpacking, the code looks like this:


![Meterpreter payload after unpacking](/images/2019/05/payload-1024x383.png)

Without diving into details it is a PowerShell code injecting a particular shellcode (the long base64 string) into the memory. However, all the artifacts that we are interested in are in the shellcode itself. Therefore we can decode and disassemble it with any x86 disassembler (CyberChef also has this option). After going through code that mostly resolves required WinAPI functions, finally, we can see that it pushes two 32-bit values on the stack:

![](/images/2019/05/image006.png)

They are related to WinSock API data structure sockaddr (more info here: [https://docs.microsoft.com/en-us/windows/desktop/WinSock/sockaddr-2](https://docs.microsoft.com/en-us/windows/desktop/WinSock/sockaddr-2)). First value from top is an IP address (be careful bytes are reversed on disassembly!) and the second one is a port and a constant 0002 (AF\_INET) which indicates it is a TCP/IP stack. If you decode these values you will get the port and the IP.

There is also an x64 version of this payload, it looks a little different on disassembly because of a different calling convention for x64 architecture:

![](/images/2019/05/image007.png)

Note that here the entire structure is moved to the stack (not pushed) as a single QWORD (64-bit value)

I created a CyberChef recipe that allows to extract IP address and port from both 32 and 64-bit versions.

```
{"op":"Regular expression","args":["User defined","[a-zA-Z0-9=/+]{30,}",true,true,false,false,false,false,"List matches"]},{"op":"From Base64","args":["A-Za-z0-9+/=",true]},{"op":"Gunzip","args":[]},{"op":"Regular expression","args":["User defined","[a-zA-Z0-9=/+]{30,}",true,true,false,false,false,false,"List matches"]},{"op":"From Base64","args":["A-Za-z0-9+/=",true]},{"op":"To Hex","args":["None"]},{"op":"Conditional Jump","args":["68([0-9a-f]{8})680200([0-9a-f]{4})",false,"standard",10]},{"op":"Conditional Jump","args":["49bc0200([0-9a-f]{4})([0-9a-f]{8})",false,"reverse",10]},{"op":"Label","args":["standard"]},{"op":"Regular expression","args":["User defined","68([0-9a-f]{8})680200([0-9a-f]{4})",true,true,false,false,false,false,"List capture groups"]},{"op":"Split","args":["\n",":"]},{"op":"Subsection","args":[":([0-9a-f]{4})$",true,true,false]},{"op":"From Base","args":[16]},{"op":"Merge","args":[]},{"op":"Subsection","args":["^([0-9a-f]{8}):",true,true,false]},{"op":"From Hex","args":["Auto"]},{"op":"To Decimal","args":["Space",false]},{"op":"Split","args":[" ","."]},{"op":"Jump","args":["finish",10]},{"op":"Label","args":["reverse"]},{"op":"Regular expression","args":["User defined","49bc0200([0-9a-f]{4})([0-9a-f]{8})",true,true,false,false,false,false,"List capture groups"]},{"op":"Split","args":["\n",":"]},{"op":"Subsection","args":[":([0-9a-f]{8})$",true,true,false]},{"op":"From Hex","args":["Auto"]},{"op":"To Decimal","args":["Space",false]},{"op":"Split","args":[" ","."]},{"op":"Subsection","args":["^([0-9a-f]{4}):",true,true,false]},{"op":"From Base","args":[16]},{"op":"Label","args":["finish"]}]
```

It can also be found here:  
[https://github.com/lasq88/CyberChef-Recipes/blob/master/README.md](https://github.com/lasq88/CyberChef-Recipes/blob/master/README.md)

Unfortunately, CyberChef seems to be a little bit bugged lately (regular expressions don’t load correctly) and it seems to have some issues with branching so I also created a simple JavaScript tool for the same purpose. You can find it here:

[https://github.com/lasq88/IR-Tools/blob/master/meterpreter.html](https://github.com/lasq88/IR-Tools/blob/master/meterpreter.html)

It is a standalone script so you can launch it in any browser (tested in Chrome though), paste a meterpreter payload, press Extract IP and it should work.

That should be working for most default meterpreter payloads, although I did not test it enough to be sure. Also for any custom lateral movement payloads this will most likely break.