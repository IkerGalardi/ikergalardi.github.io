---
title: Everything is a file (descriptor)
date: 2023-12-13
draft: false
tags: ["posix", "api", "unix"]
---

# Everything is a file (descriptor)

Im sure that most of you who use (or have studied) unix like operating systems like linux or the BSDs know about their philosophy. But when you really think about it, what is that file descriptor thingy? And why would everything be a file?

Lets find out!

## The origin... unix!
As always, everything old about computer things has to be related to unix. You dont trust me? Well what about time management? Have you heard about the the unix time? What about C? And the posix API? I hope that you can now understand why Im talking about unix.

Unix developer had this funny idea of having access to everything on a computer via files in the file system. Want to access the terminal? Well, just interact with `/dev/tty` file in the filesystem. Want to interact with the printing device? Just use the `/dev/lp` (short for Line Printer maybe?). Want to check what devices are connected to the machine? Simply ls /dev/! Magical right?

NOTE: Other systems such as microsoft have similar mechanisms by having a separate magical file system on \Devices. But isnt accessible from the users perspective.

Looks great from the terminal's point of view, but how are those files used?

## Unix filesystem API
Accessing files in a unix program is really simple! Just open the file, read or write whatever buffer and the kernel will take care of the rest!

The next are the functions used for that:
- `open`: given a path and intentions (want to write, read, both?), open the file and return a file descriptor (that descriptor thing again!)
- `write`: given a file descriptor and a buffer, write that buffer to the file represented by the file descriptor.
- `read`: given a file descriptor and a buffer, read data from the file represented by a file descriptor.
- `seek`: given a file descriptor and a position, move the cursor to that point. The function returns the new position, so by not moving the cursor you can use the same function to retrieve the cursor position.
- `close`: given a file descriptor, closes the file refered to by the filed descriptor. Its more of a hint to the OS telling it that were no longer using the file.

Cool, but how do you tell the terminal device that you want to write characters to the screen? Isn't it obvious (and beautiful)? Just use the above functions and the OS will do its magic and it *Just Works™*. Even sockets are file descriptors that can use those functions (although `send`/`recv` are preferred to `write`/`read`).

Nice! Simple! Some even might say elegant! Thats until you want to, for example, retrieve the terminal size... Just use read! Well, then how are you going to differentiate someone typing on the terminal vs retriving terminal information! You could create some kind of protocol to comminicate with the terminal, so a convination of write *GetTerminalSize* packet + read *TerminalSize* packet could solve it, but thats too ugly and cumbersome...

So what if we add some kind of swiss army knife function used for these kinds of situations where the semantics of `read`/`write`/`seek` break? The unix guys basically created something called `ioctl` (IO control for short, pronounced ioctal by psychopaths) that basically takes a buffer as input and outputs a buffer. Giving total freedom to the specific device on how to interpret those buffers. The real function also takes an additional command parameter to simplify the driver implementors lives.

With this, we could use the ioctl function passing the `GetSize` command and receive the terminal size on the output buffer.

## Blocking and synchronization
When reading from a file descriptor, the process gets blocked until the data is available. In the case of files, until the disk data is actually on the main memory; whereas in the case of sockets until some data has arrieved from the network. What about devices? It totally depends on the driver.

So what happens when a network server needs to listen from multiple sockets at the same time? We need a synchronization mechanism to wait on multiple sockets and when data arrieves, tell us where we should read. Thats when an ancient function called `select` was created.

You can basically pass a maximum of 1024 of file descriptor, and the process will get blocked until something happens! Briliant. Later other interfaces like `poll` (and an extended linux specific version `epoll`) came in to circumbent all the shortcomings of select.

## What else does use file descriptors?
There is another really handy interface that is entirelly based on file descriptors... inotify! Inotify is an API used basically for getting notifications when files change. With this API you can get file descriptors from which you can read from changes in metadata to changes in the file data itself. The usage of `select`, `(e)poll` is basically obligatory when trying to keep track of multiple files.

As such, there are more file descriptor based APIs: timerfd, pretty self explanatory; memfd to use (and share) RAM memory with the usual `read`/`write` API.

## Event loops
This might seem like a deviation in the topic of the article, but hear me out. What if we create a event loop by using the aforementioned primitives? We could treat all the reads from file descriptors (file modifications, accepting connections, etc) as events and treat kernel level facilities in a well known paradigm.

For example, if we want to create a webserver that caches all the documents but at the same time supports hot reloading (something like what hugo does with the `hugo serve` command), we can do that by simply listening to a socket and waiting for inotify events at the same time.

## Even't
This seems fun, why don't we write a debugger now! We could wait for user input and traced process events by using select... you have been baited. Ptrace (the linux debugging API) and in fact the whole process management API ditches this file descriptor stuff in favour of using a new synchronization mechanism, the `wait` function.

With this inconcistencies you just make it harder for system developers. You can't just wait for events from the kernel on a single point, you are forced to have multiple threads. Maybe threading is not a must, an there is some kind of trickery, but I dont even care about tricks, I just care about consistency and how straight forward the developer experience is.

As mentioned before, the whole process management API is inconsistent. So if, for example, you want to create a service management program that has a socket to listen for commands, and manages services by restarting them when they crash; you need to have two event loops (one for receiving data from the socket, and another for child process' events).

## How do we improve this?
This is probably not going to change on the posix/unixy world. Posix2 might be able to solve this issue, but in the mean time, what can we do with our current APIs? Let's propose a solution!

In similar ways to the memfd and timerfd APIs, why don't we create a procfd familly of functions that fixes the synchronization inconsistencies?

First, we need to define a way to retrieve one of these proc file descriptors. Following the timerfd way, the easiest solution would be to create a `procfd_create` function that takes the process id as an argument. I would argue that this is the most straight forward way to design an API, but I would go one step further and create the file descriptor by opening the `/proc/<pid>` directory.

> NOTE: Aparently there is a similar interface called `pidfd` with witch you can `pidfd_open` a process id to get a file descriptor related to the process. Includes functions like `pidfd_send_signal` to replace the traditional API.

Now with this file descriptor, socket like semantics can apply to the `(e)poll`/`select` functions and the event loop would function as expected! Ptrace (and process related functions) can be turned into `ioctls` in order to improve consistency. Of course, the "old way" of doing things doesn't need to be removed, as that would break compatibility for no reason. Maybe posix2 can remove those instead of just marking them as deprecated.

## Conclusions and possible experiments
It would be nice to create some kind of experiment where a kernel could be modified in order to provide the mentioned alternative and test real benefits on the mentioned API improvements. The changes could be simple syscall additions that would redirect, for example, the ptrace related procfd ioctls to the real ptrace syscall functions. But that's a proyect for another time!

I really think that having a more consistent event loop like structure to programs can help. Event loops are widely used on the GUI and gaming side of programming, and they expose a simple and easy way to react to events on the system. Who knows, even system programmers can benefit from this in the near future!