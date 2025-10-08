---
title: "From the archive #2: Ursnif dropper deobfuscation"
date: 2021-11-25 05:47:11
draft: false
categories: ['Deobfuscation', 'Dropper', 'JavaScript', 'Malware analysis', 'Ursinf']
tags: ['deobfuscation', 'dropper', 'javascript', 'malware', 'python', 'ursnif']
---

In this article, I want to show a simple approach to JavaScript deobfuscation, based on an older Ursnif dropper sample. This is part 2 of my "From The Archive" series, where I release older reports lying on my disk. I hope you will enjoy and learn something from this post.

![](/images/2021/11//deobfuscated-1024x757.png)

<!--more-->

Ursnif downloader deobfuscation

# File info

**MD5:** c2e5e715f6705604f8a6df3562476463  
**SHA-1:** f3767818906b5dd595d720ace681a1787c0fadde  
**SHA-256:** 18f3a39bf2d85e889ed24be30dc18fd5048b4c7dd32103f4d97b7a08ade3a973  
**Filename:** presentation\_r9p.js  
**VirusTotal**: [https://virustotal.com/gui/file/18f3a39bf2d85e889ed24be30dc18fd5048b4c7dd32103f4d97b7a08ade3a973](https://virustotal.com/gui/file/18f3a39bf2d85e889ed24be30dc18fd5048b4c7dd32103f4d97b7a08ade3a973)

# Deobfuscation

The initial file is quite huge, as it consists of 3 771 310 characters. It can be overwhelming but as we will soon see, the obfuscation method is pretty straightforward. As always we start with beautifying JavaScript code so we can see more than one line of almost 4 million characters. Any JS beautifier can be used, I always recommend Sublime Text 3 with HTMLPrettify plugin as Sublime is overall a very good text editor to use when deobfuscating any (non-binary) code.

After beautifying the code it now has 579 lines of code. It still has an overwhelming number of almost 4 million characters. Fortunately, one thing stands out, these are huge comments near the end of the file. We can remove them with one simple  regular expression:

/\\\*\[0-9a-z,\]\*\\\*/

<figure>

![](/images/2021/11//comments-1024x165.png)

<figcaption>

Removing comments with regular expression

</figcaption>

</figure>

That way we removed almost half of the characters from the file leaving us with a still huge file of 1 705 877 characters. However, if we look at the preview of the file (for example in Sublime on the right) we can see a clear structure in the file.

Indeed, we can divide this file into 3 parts:

1. Variable declarations (lines 1 – 399)
2. function declarations (lines 400 – 575)
3. Function calls (lines 576 – 579)

We can divide the variables part into additional two parts. From lines 1 to 256 we have variables that are assigned a single 3-digit numerical value.

![](/images/2021/11//vars.png)

Later from lines 257 to 399, we have declarations of arrays that consist of variables declared before as numeric values. If we check it, these arrays make up 99% of our huge file by being 1 691 920 characters long. Spoiler alert: as we will later see, each position in the array corresponds to one byte in the final binary dropped to disk.

![](/images/2021/11//arrays-1024x44.png)

The last declared variable is “rbx” which gets a value of some obfuscated environment variable (later we will see it is a path to the TEMP folder)

![](/images/2021/11//rbx-1024x29.png)

After this big part of variable declarations, we have a few function declarations. I will go through them one by one.

<figure>

![](/images/2021/11//LvREnzDD-1024x115.png)

<figcaption>

LvREnzDD function

</figcaption>

</figure>

The first function is called LvREnzDD and it takes one argument. It is quite long so I won't paste here the entire transcript. It is not very obfuscated and its purpose seems clear at the first sight. Nevertheless, some important values are obfuscated by using another function (LmvCS) which we will describe in a second.

LvREnzDD creates two ActiveXObjects. It then uses the HexToStr function (also declared later in the file) on earlier declared arrays and writes output to one of these objects. Later it copies the value of the first object to the second object and saves it to the file. The filename is passed as an argument to the function. To simplify matters: this function decodes those big arrays above and writes their decoded value to the file on disk.

<figure>

![](/images/2021/11//TjeMxMNjl-1024x76.png)

<figcaption>

TjeMxMNjl function

</figcaption>

</figure>

The next declared function is called TjeMxMNjl. It takes two arguments and it is very simple. It creates a text file with the name passed as the second argument, and then it writes the value of the first argument to the just created file.

<figure>

![](/images/2021/11//LmvCS.png)

<figcaption>

LmvCS function

</figcaption>

</figure>

The next function called LmvCS is quite important, as it is used extensively within the code to obfuscate important pieces of information. It is quite simple as it takes 1 argument which needs to be a list of numerical values. It then iterates over that list, subtracts 101 from each value (just an additional layer of obfuscation), and then converts these values to ASCII strings using a built-in function fromCharCode and simple concatenation.

<figure>

![](/images/2021/11//HexToStr-1024x46.png)

<figcaption>

HexToStr function

</figcaption>

</figure>

<figure>

![](/images/2021/11//decode-1024x103.png)

<figcaption>

decode function

</figcaption>

</figure>

The next two functions I will discuss together as they make sense only used together. Function decode takes one argument which is a list of numerical values, it subtracts 101 (we know why already), and then, despite its name it encodes it as a string of hexadecimal values.

Function HexToStr takes a list of numerical values and uses function decode to transform them to hexadecimal string only to decode it later to ASCII string format.

In the end, this is only additional obfuscation as the result of the HexToStr function is identical to the result of the LmvCS function described before. It takes a list of encoded numeric values and decodes them to ASCII string (actually extended ASCII as it can take any values from 1 to 256 – as we will see this is used in earlier described LvREnzDD function to write binary data to a file so it makes sense to use extended ASCII values).

<figure>

![](/images/2021/11//YmBUcxJWuaW-1024x47.png)

<figcaption>

YmBUcxJWuaW function

</figcaption>

</figure>

The next function called YmBUcxJWuaW is also pretty straightforward. It takes one argument, it creates a new Wscript shell instance (not even obfuscated), and then it runs an obfuscated command, part of which is a function argument. As we will later see, the argument is just a filename.

<figure>

![](/images/2021/11//MkOCHAqHlW-1024x59.png)

<figcaption>

MkOCHAqHlW function

</figcaption>

</figure>

The last declared function is similar to the previous ones. It creates an obfuscated ActiveXObject, then in the context of this object it checks if the file (which name is passed to the function as an argument) exits. If it does the entire script quits.

<figure>

![](/images/2021/11//function_calls-1024x90.png)

<figcaption>

function calls

</figcaption>

</figure>

The last 4 lines of the script are functions calls. Unfortunately, all argument values are obfuscated so we need to deobfuscate them first to fully understand these commands.

How do we approach deobfuscation? It is quite simple. There is only one obfuscation technique used here as you might have already noticed. Every character of any important string is represented as ASCII numeric value + 101 and stored in one of the variables declared at the top. Function LmvCS is used to deobfuscate them when the script is running.

The same thing is done for bytes of final binary dropped to the disk using the HexToStr function.

To deobfuscate the code we will write a simple python script. It will not only deobfuscate the entire script but will also drop the final payload to the disk and calculate its hash.

<figure>

![](/images/2021/11//python_code-1024x954.png)

<figcaption>

Python deobfuscation code

</figcaption>

</figure>

Here is the python code: I hope it is pretty self-explanatory with all the comments but I will write a few lines. It goes through the obfuscated files line by line. It uses regular expressions to find values of variables containing encoded ASCII numbers. It stores them in the dictionary for later use. It also uses regular expressions to find all arrays containing bytes of the final binary. It then uses a function identical to LmvCS from the dropper to decode these characters and convert them to deobfuscated strings. It replaces obfuscated strings from the script with unobfuscated ones. It also decodes a final binary and stores it to the disk as “second\_stage.bin”. Additionally, it calculates MD5 of this binary.

<figure>

![](/images/2021/11//deobfuscated-1-1024x757.png)

<figcaption>

Deobfuscated code

</figcaption>

</figure>

After some cleaning and renaming for clarity this is the final output:

As you can see I renamed functions to better describe their functions:

- MkOCHAqHlW → check\_flag
- TjeMxMNjl → create\_flag\_file
- LvREnzDD → write\_to\_file
- YmBUcxJWuaW → execute\_binary

This is a pretty straightforward dropper without many additional capabilities. It first checks for the existence of VsfcfCZ.Rcragic file in %TEMP% folder. If such a file exists dropper will exit to not infect the same machine twice. If such a file does not exist it will create it with "aagZotnGtzY” as file content. It will then store the final payload to %TEMP%\\BkFEx.txt and execute it.

As you can see our python script also dropped the final binary to disk for analysis and it calculated the MD5 hash (bde2ca59a5d133fcaed6bfb7a22ebf08). We can check on VirusTotal that the final payload is indeed Ursnif.