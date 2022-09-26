---
title: How not to write performant code
date: 2022-09-26
tags: ["allocator", "project"]
---

Don't you feel like `malloc` is really slow? Most probably not, as the `malloc` implementation shipped on most standard libraries are probably older than me. Still, a fool past of myself thought that I could in 3 moths achieve what glibc achieved in most certainly triple the time. This is the story of how I ended up writing a memory allocator for my end of degree project for university.

For the last 5 moths I have been writting a hybrid memory allocator using the [SLAB](https://people.eecs.berkeley.edu/~kubitron/courses/cs194-24-S14/hand-outs/bonwick_slab.pdf) allocator used on most operating system kernels and what the operating system provides in order to accelerate memory allocations. The idea was... if the SLAB allocator has brought impressive performance improvements on the linux kernel, why can't it have the same performance improvements but for userspace applications? I still think that that's a pretty good premise for a project, but still, the project was a bit of a failure on my heart.

After several ideas shared with my tutor, the one that we ended up working on was the slab allocator but for userspace. Meaning, that I needed to write a memory allocator (for the first time), and it needed to be **FAST** so I could beat GNU. The project ended up being a fight between me and callgrind/perf in order to discover what was the performance bottleneck on a function that had less than a millisecond of execution time.

For everyone trying to enter the optimization world, let me tell you several MUSTs in order to have an easier time:

- First, have some reliable performance numbers. Without having performance numbers nor something to test performance you are blind in the face of the problem. Having something to test the performance on makes you focus on the important parts of the code and not go blindly.

- Test multiple scenarios and go after the worst case. At the start of the project I had a simple benchmark that did mass allocations. After some tuning of the code, the performance was looking promising, but like I realized later, this was a small view on the whole story. After digging on the internet for allocator benchmarks, I realized that most of them put enphasis on the ordering of allocations and patterns. As it turns out, that was a very important factor when facing real world applications, and thus, the performance tuning done before was useless as the focus was on the wrong place.

- Avoid early optimizations. As it was on my case, I had to build the entire allocator from scratch (with performance in mind). Too early in the development I ended up optimizing several structures and functions, which made the entire structure of the project shift before even having all the features needed, making them difficult to be added later. Optimizing the code should be done after having all the features.

- Last but not least, know your tools! Knowing how to work with perf/callgrind and knowing their strengths and weakneses helps make better decisions. This is what I learned with this project: use perf at the start to see the main problem, later dive in the code using callgrind. Callgrind lets you see in better detail how your algorithms are executing so you can easily see if you are doing stupid things. Perf on the other side, lets you see the functions taking the most time (big hint) and hardware specific stuff like branch predictor or cache misses. Don't use just one, they have different strengths.

After all the things learned, it wen't smoothly and the performance was good right? Wrong, it was too late already. The time given for the project was to small, and even though I ended up spending much more time than the permitted, the performance did not improve much. Still, I ended up with a 10, so my writting skills compensated for my coding skills 😉.

It was a fun adventure, and I don't regret anything about the project, but still, next time I try to write good performant code, I'll take my own advice.