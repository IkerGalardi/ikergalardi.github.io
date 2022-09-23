---
title: Thoughts on the linux desktop
date: 2022-03-08
tags: ["linux", "rant"]
---

# Thoughts on the linux desktop

Due to some hardware changes on my setup I’ve realized some issues regarding the current situation with the linux desktop (and distributions in general). So with this article I’ll try to explain my thoughts and propose some changes.
Normal desktop usage

Let’s start analyzing the whole windowing stack… xorg or wayland? Wayland, being new in the neighborhood has a more modern and secure approach, but stability is lost due to new “untested” code being written. The most notable security features are that no input events like keyboard presses are sent to non focused windows and lack of screen recording. Of course, we all want to be secure with our computers, so basically removing the existence of keyloggers would make us happy, right? Wrong! This approach makes shortcut daemons completely useless, and screen recording is completely broken… Yay! Apart from that, as wayland is not a server (is just the specification), the entire implementation responsibility becames part of the desktop environment/window manager developers, fragmenting the implementation. This does not seem wrong at first, but as I discovered recently with graphics programming, small differences in drivers can make applications run on one machine and crash on others (this does not happen right now as I’m aware, but as more wayland compositors start being built with the time, I predict this will be a problem). But of course not all the things are issues, as seen with comparisons between GNOME xorg and GNOME wayland, the performance and battery life benefits are big (pipewire also solving the screen sharing issue); so it seems that it’s the future.

Audio is another big issue in the linux desktop, as pulse has been buggy and unpredictable from the start. Many users report that pulse sometimes forgets the audio configurations and defaults randomly (although I haven’t experienced that) and random crashes. For me the most annoying things are that pulse is not capable of maintaining Bluetooth devices and starts randomly changing into the speakers, or pulse being unable to detect the microphone array of my laptop and sounding like a 50 year old microphone.

And last but not least… please we have hardware acceleration on modern computers, let’s use it! Looking at a PDF document or seeing a youtube video should not suck up my battery as hard as it does!
Developers perspective

Let’s bring the distribution fragmentation topic again. Some people say that’s not a concern because they link all their applications statically (shame on you if you are on that group), others exaggerate saying that glibc breaks every release (that’s a lie, it breaks every two releases), and others fell in love with flatpak and don’t see beyond that. As always with everything, real life is more complicated than all those points of view. All points of view have their point (forgive the repetition).

Remember LMake? Well, when I tried to build a single binary for all distributions (at least distributions installed by my friends), some random problem arose… The c++ standard 17 was implemented on both arch and void’s installed libraries, but as my application was built using a newer version of glibc, so the dynamic linker refused to use the installed libc and gracefully exited with a completely understandable error message (forgive the irony). When a developer uses a standard, it expects that all the versions of the library that implement that standard will work (maybe not perfectly because unintentionally relaying on bugs, but at least try to work). So what do most developers do? Recompile the application for each distribution or statically link everything in the world into a big fat binary executable (shame on you Rust). What’s the solution? I don’t really know, but it is still a problem to solve anyway.

To solve the before mentioned problem, AppImages where created, where they keep all the libraries they use in an embedded filesystem. This makes more sense than statically linked applications because you can embed configurations inside, making the application movable between distributions/computers maintaining the same look, feel and configurations. Of course, this has the same issues as the big fat statically linked binaries.

Then, the flatpak team came with a solution… Runtimes! These runtimes are a collection of libraries that are common enough that can be used between applications, but still giving the chance to use specific library versions included on the flatpak bundle. Apart from that, they also implemented sandboxing, Yay! More security! Of course, not all is perfect, as it makes very difficult to change internal configurations for applications and sometimes the desktop theming is not picked up as well as users expect.

Most distributions are still reluctant to use this universal packages like flatpak, and still use their traditional dependency hell based package management. I’ve seen the dependency graph of Xorg…. And I haven’t slept well since then… I still have nightmares…
Conclusions

Well, as explained, linux desktop is the worst thing I ever have seen… Not really, I still prefer it over Windows, as it has many advantages I have not talked about (and probably don’t even realize). I still recommend linux to new users (don’t be scared of the learning curve please).

Still, I want to try to solve some of the before mentioned issues with my next long term project. Still on the thinking and planning stage, but stay tuned if you are curious. See you next time!
