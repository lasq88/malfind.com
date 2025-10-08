---
title: "How I accidentally found a clickjacking feature in Facebook"
date: 2018-12-21 14:00:37
draft: false
categories: ['Bug bounty', 'Clickjacking', 'Facebook', 'Websites']
tags: ['bugbounty', 'clickjacking', 'facebook']
---

I would've never thought that one of my first blog posts will be about looking for bugs in Facebook. I don't consider myself a bounty hunter, and had never actively looked for bugs. I focus mostly on Incident Response, Forensics and Malware Analysis. To my surprise then I am sharing this particular story with you. It's about my first bug report, a short spam campaign and a strange Facebook feature.

So, yesterday there was this very annoying SPAM campaign on Facebook, where a lot of my friends published a link to what seemed like a site hosted on AWS bucket. It was some link to a french site with funny comics, who wouldn't click it right? 

![One of the SPAM links](/images/2018/12/spam.png)

After you clicked on the link, the site hosted on AWS bucket appeared. It asked you to verify if you are 16 or older (in French) in order to access the restricted content. After you clicked on the button, you were indeed redirected to a page with funny comic (and a lot of ads). However in the meantime the same link you just clicked appeared on your Facebook wall. How is this possible?

![Cickjacking page](/images/2018/12/spam1-1024x608.png)

After looking at the page source I spotted a suspicious iframe tag, which smelled of a clickjacking. This frame led to another AWS hosted page, which led to another which in the end led to the following facebook url (I changed a destination URL for obvious reasons):

```
https://mobile.facebook.com/v2.6/dialog/share?app_id=283197842324324&href=https://example.com&in_iframe=1&locale=en_US&mobile_iframe=1
```

This link, when pasted into the browser leads to a typical "share a page" window you may know from Facebook (although you may need to change `app_id`, as it was removed). However if we look into the response headers, this page have a properly set X-Frame-Options: DENY header, so it shouldn't be susceptible to a clickjacking attack. Strange.

![Suspicious iframe code](/images/2018/12/iframe-1024x505.png)

I was trying to reproduce this attack in every most popular browser (Chrome, Chromium, Edge, IE, Firefox) but I only confirmed what I already knew. Trying to load this specific iframe in the browser everytime raised a X-Frame-Options error.

![Correct Chromium behavior](/images/2018/12/x-frame-chromium-1024x217.png)

I was a little bit stuck at this point, but these posts kept appearing on my Facebook wall, so it had to work for an attacker. Funny thing is that in the meantime the attacker banned Polish users from his site redirecting them to the nonexistent domain (with Polish swear words in it, so he was definitely Polish). It seems that he targeted this campaign on French Facebook users but he had too much traffic from Poland. At least this is what I assume.

![Simple geolocation script to ban victims from Poland](/images/2018/12/pl_ban-1-1024x361.png)

After some time and some ideas, I figured out that victims doesn't have to use a desktop browser, especially with even url from iframe giving me a clue with its "mobile." subdomain. I launched this in the Android Facebook App and miraculously it worked! The X-Frame-Options header was totally ignored.

![Working iframe on Android Facebook App](/images/2018/12/iframe_working-1024x285.png)

Strangely enough it didn't work if I tried to put in iframe any other part of protected content (like a settings page for example). It seems that Facebook inbuilt browser chose to deliberately ignore the X-Frame-Options header only for this particular API call.

I dug a little in Facebook Developer documentation and it seemed it may be "not a bug, but a feature". On [this doc page](https://developers.facebook.com/docs/sharing/reference/share-dialog) we can learn about a special parameter called `mobile_iframe` which *"if set to true the share button will open the share dialog in an iframe on top of your website [...] This option is **only available for mobile**, not desktop"*. It seems then that this is indeed a feature but a very poorly implemented one.

**Update [22/12/2018]:** After a verification, a real issue is that if you are connected from a mobile device, Facebook doesn't even set an X-Frame-Options header for this site. So this is indeed a feature. They also include a substitute security precaution against clickjacking for mobile users, a pop-up confirmation to ask if you really want to share this link. As this campaign proved, it is not very effective.

Nevertheless I reported this to the Facebook Bug Bounty program, although I was quite sure this will be rejected as "working as intended" but I didn't want to publish this post without giving them chance to fix this. This was my first ever bug report so I was quite excited anyway. As expected Facebook declined the issue, despite me trying to underline that this has security implications. They stated that for the clickjacking to be considered a security issue, it must allow attacker to somehow change the state of the account (so for example disable security options, or remove the account). On the bright side I am very pleased with their reaction time and swift response, all matter closed within 12 hours from an initial report.

In my opinion they should fix this, but since they declined it I have no moral issue to publish this article. Maybe it will help to better highlight this problem.  As you can see this "feature" can be extremely easily abused by an attacker to trick Facebook users to unwillingly share something on their  wall. I cannot stress enough how dangerous this is. This time it was only exploited to spread spam, but I can easily think of much more sophisticated usage of this technique. Just imagine how much damage can a link to a malware document or a phishing site cause when shared by a well-known person with thousands of followers. In the end we all trust our Facebook friends and gurus, don't we? 

Btw. if you want to reproduce this, here is a little PoC instruction:

**Update [22/12/2018]:** As Reddit's user yessirman123 rightfully noticed, this PoC is not fully exploitable, as there is one security precaution included by Facebook. If you are connected from a mobile device, it asks you to confirm if you really want to share this link in a new pop-up window. So far I am not sure how the campaign author got around it.

**Update [23/12/2018]:** According [to this ZDNet article](https://www.zdnet.com/google-amp/article/researcher-publishes-proof-of-concept-code-for-creating-facebook-worm/) Facebook states they improved their clickjacking detection "earlier this week". So yesterday I took a full clickjacking site out from the Edge cache, and rebuilt it. It didn't work, the pop-up confirmation still appears. So possibly Facebook improved they detection mechanism and introduced this pop-up confirmation after the attack?

```
1. Register a new Facebook App
2. Publish it and turn on the API
3. Create a new website with following html code:

<html><body><iframe style="margin-top: -300;width: 100%;height: 340px;" id="tenframe" src="https://facebook.com/v3.2/dialog/share?app_id<your_app_id>&href=https://example.com/?fbclid=IwAR3lPfy4rsBLWdSRVGNcwNmWt7hUV7ykCew5AllWes941oW37PIupZdMGpM&in_iframe=1&locale=en_US&mobile_iframe=1" scrolling="no"></iframe></body></html>

where you change <your_app_id> to your app id of course

4. Publish a link to this website on a facebook wall
5. Click on the link from a Facebook App on Android - you will see it loads an iframe without any issue
```