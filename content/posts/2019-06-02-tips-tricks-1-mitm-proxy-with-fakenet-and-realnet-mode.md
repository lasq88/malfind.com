---
title: "Tips & tricks #1: MITM proxy with fakenet and realnet mode"
date: 2019-06-02 08:26:36
draft: false
categories: ['Malware analysis', 'Tips &amp; tricks']
tags: ['burp', 'fakenet', 'inetsim', 'linux', 'malware', 'mitm', 'proxy', 'realnet', 'vm']
---

This post will be the first of quick tips & tricks series. I don't have the time, and to be honest nor the inspiration lately to write longer in-depth posts as I would like to. Therefore I will stick to shorter forms, hopefully this will make this blog a little bit more alive.

In this short tip, I would like to share with you my setup for a Man-in-the-Middle proxy for my malware analysis lab. When porting my lab to the new machine I had to reconfigure few things, and to my surprise I found out that there seems to be no good tutorial to correctly set a MITM proxy for malware analysis.

There are multiple tutorials showing how to set up a malware lab with a fake net and HTTPS interception using both inetsim and burp. You can find them here:

- [https://blog.christophetd.fr/malware-analysis-lab-with-virtualbox-inetsim-and-burp/](https://blog.christophetd.fr/malware-analysis-lab-with-virtualbox-inetsim-and-burp/)
- [https://medium.com/@atomixgray/basic-malware-lab-a021a6d639cb](https://medium.com/@atomixgray/basic-malware-lab-a021a6d639cb)
- [https://medium.com/@eaugusto/32-bit-windows-kernel-mode-rootkit-lab-setup-with-inetsim-e49c22e9fcd1](https://medium.com/@eaugusto/32-bit-windows-kernel-mode-rootkit-lab-setup-with-inetsim-e49c22e9fcd1)

Because of them I won't be making another tutorial how to set up your lab. You can use tutorials above. If you are curious, I am using a very similar setup with Flare VM on my main Windows 10 box and an intercept router based on Debian with both fakenet and realnet modes (which I will explain later).

<!--more-->

#### Burp port redirection

Before diving into details of setting up the multimode mitm proxy I would like to share a smaller tip, which may be useful if you follow tutorials linked above. They are good tutorials and I also followed them when setting up my lab, but there is one thing that in my opinion you should change in this setup.

If you configure your burp to redirect to localhost as per instructions above, the fakenet connection to inetsim will work correctly however due to burp interpretation of these redirected packets, it will list all of the connections from your infected box as localhost.

<figure>

![](/images/2019/06//burp-localhost-1024x549.png)

<figcaption>

Burp listing all connections as localhost in default configuration

</figcaption>

</figure>

The only way you can distinguish between connection targets in this setup is by looking at the host header of each request. Due to the amount of http traffic that Win10 box is generating this may be a tiresome task.

Fortunately a simple trick exists to get around that. If you have your inetsim set up to listen on 0.0.0.0 then you don't actually have to redirect to localhost. Burp allows you to redirect only ports, just leave the host option empty and burp will redirect only port. As inetsim is listening on every interface it will grab this traffic anyway. Although if you have 2 interfaces up it may not work every time as I will explain in next section. So it is advised to have only 1 interface up in the fakenet mode.

<figure>

![](/images/2019/06//burp-nohost.png)

<figcaption>

Burp correctly set up to redirect only port

</figcaption>

</figure>

<figure>

![](/images/2019/06//Screenshot-from-2019-06-02-15-55-20-1024x545.png)

<figcaption>

Correct redirection to inetsim

</figcaption>

</figure>

#### Fakenet and realnet

Second thing that irritated me in this setup was lack of ability to actually simply redirect malware traffic to internet but keeping the ability to peek into https traffic. Sometimes you just want malware to download this second stage payload or want to eavesdrop on communication with C2. Then you want to have an easy switch from fakenet to realnet. This is actually a simple reconfiguration, and it can also be achieved with the same setup we had before, just changing config files for burp and inetsim.

First thing you have to do is of course to connect the linux box to the internet. Just enable second interface on your hypervisor in NAT mode and linux should automatically route all traffic from internal network to internet via hypervisor. If this is not the case, you might want to set up your NAT gateway as default gateway.

<figure>

![](/images/2019/06//realnet1-1024x371.png)

<figcaption>

Double interface setup

</figcaption>

</figure>

Second step is to modify an inetsim config so it will act only as a DNS server forwarding all traffic to burp. Just grab the old inetsim config, copy it and remove all services from it except for DNS. Save it with a different name and it should be fine.

<figure>

![](/images/2019/06//realnet2.png)

<figcaption>

InetSim acting as DNS only

</figcaption>

</figure>

Third and last step is to modify burp to act as standard MitM proxy, forwarding all requests to the internet. The only thing you have to change is port you forward a request to, routing table will take care of the rest. You may want to save your realnet burp config in a different file.

<figure>

![](/images/2019/06//realnet3.png)

<figcaption>

Burp setup to forward requests to internet

</figcaption>

</figure>

That's all! You should now be able to redirect traffic from your malware box to internet, keeping the burp mitm proxy in between.

<figure>

![](/images/2019/06//realbnet4-1024x497.png)

<figcaption>

Burp in MitM mode - redirecting traffic to the internet

</figcaption>

</figure>

Now you just have to do a few simple steps on your linux machine to switch from fakenet to realnet and back.

To switch from fakenet to realnet:

1. Bring NAT interface up
2. Restart InetSIM with DNS-only config
3. Load realnet config into Burb

To switch from realnet to fakenet:

1. Bring NAT interface down
2. Restart InetSIM with all services simulation config
3. Load fakenet config into Burp

Done! You can even write a script for this if you have a need, although it is simple enough to just do these 3 things manually.

Enjoy your mitm box!