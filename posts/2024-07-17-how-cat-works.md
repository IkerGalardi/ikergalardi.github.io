---
title: Unix utilities, how cat works
date: 2024-07-17
draft: false
tags: ["posix", "api", "coreutils"]
---

# Unix utilities, how cat works

## Introduction
At university we had an *introduction to operating systems* course where we basically learnt how basic unix utilities like `cat`, `ls`, etc, worked by programming them in C using the unix API.

This course was kind of mind blowing as I never touched such low level APIs, and kind of broke the illusion that system's programming involves some kind of black magic and Einstein level brainpower. So with this article series I want to re-remember those lessons in the hopes that someone can also break that barrier to learning this kind of low level stuff.

For this, as the first step in this journey, I have chosen `cat` as the utility to reproduce as it's the simplest one that will lead as an introduction to file descriptors and file system system calls.
## What the hell does `cat` actually do
First and foremost, its important to know what we actually want to implement, so lets read what the [posix specification](https://pubs.opengroup.org/onlinepubs/9699919799.2018edition/) has to tell us about `cat`:

> The _cat_ utility shall read files in sequence and shall write their contents to the standard output in the same sequence.

Hold on, what the heck is standard output? To understand this, we first need to understand what a [file descriptor](https://ikergalardi.github.io/post/2023-12-13-everything-is-a-file/).
## File descriptors and standard output
File descriptors are a way to access low level system services like the file system provided by the kernel. Normal user processes can't directly access the disk information as that would be a security nightmare, so there is a privileged piece of software commonly called the kernel that basically handles disk reads and write.

> NOTE: I'm completely ignoring microkernels for the sake of simplicity. 

So if the kernel is the only one to read and write information to the disk, how can my web browser even download files and place them in the `Downloads/` folder? To solve this problem, some smart people decided to invent system calls, which are basically function calls but hand the control to the kernel so that it can do those privileged operations.

So, to keep it short, file descriptors are handles to files (or any kernel resource) that applications use to talk with the kernel and gather the information needed.

And what about standard output? Well, the thing is that unix systems have a little convention that states that when your process or application is launched, at minimum it will have 3 file descriptors opened: *standard input*, *standard output* and *standard error*. When an application is launched from the terminal, key presses in the terminal will be sent through the *standard input*, data sent through the *standard output* and *standard error* file descriptors will be shown in the terminal window.

> NOTE: The aforementioned file descriptors are not really enforced by the system, so an application can be launched without any file descriptors attached, or those file descriptors can be redirected to files or other programs. This is a more advanced topic that will be discussed on another article.
## Great! How do we work with those file descriptors?
Let's try to find out by first implementing the typical use case for the `cat` command and then move on and add more options. The standard tells us that the command should take an arbitrary number of paths from the command line and print them to standard output in order.

Very few steps are required in the traditional unix file system API in order to read or write into a file:
1. Open the file by using a path and the use case (read, write, both). This will return us a file descriptor.
2. Read or write to the file by using the file descriptor.
3. Close the file in order to hint the operating system we are not going to use it anymore.

Apart from that, one can also gather information about the file in question by using the `stat` family of functions.

### 1. Opening the file
To open a file we conveniently use the `open`function call:
```C
int fd = open(filepath, 0, O_RDONLY);
if (fd < 0) {
    perror("open");
    exit(1);
}
```
Let's break down what the above code snippet does. First we have a call to the `open` function that takes the next parameters:
- *path*: A path to the file to be opened. This will be taken from the command line in our case.
- *flags*: Additional flags that you can pass to the function in order to treat the file differently. Some examples are `O_ASYNC` in order to read and write information to the files asynchronously; `O_CREAT` in order to create the file when it does not exist... In our case, none of them are interesting to us.
- *mode*: The mode to open the file, this can be either `O_RDONLY`, `O_WRONLY` or `O_RDWR`. Pretty self explanatory what each of them mean.
After that, there is an if statement that checks whether the returned file descriptor is a valid one. If there is any error we simply print the error using `perror` (look it up in the man pages, don't be shy) and exit the program.

### 2. Reading/Writing information to the file
To read or write to or from a file we simply use the appropriate `read` or `write` function:

```C
char buffer[100] = {0}
ssize_t rc = read(fd, buffer, 100);
if (rc < 0) {
    perror("read");
    exit(1);
}
```

Let's break down what the above code snippet does. First we have a call to the `open` function that takes the next parameters:
- *fd*: file descriptor to read from. This file descriptor needs to either be `open`-ed or inherited from the parent process like with *standard output*.
- *buffer*: a buffer to where the read data will be written to.
- *count*: the number of bytes to read

The `read` function returns the number of read bytes, so we can use that return value to either detect if there were any errors when reading or to see how much data has been actually written.

Likewise, the write function mimics the taken parameters, but instead of reading data from disk and placing it in the given buffer, takes data from the buffer and writes the given data to the file.
### 3. Closing the file descriptor
How convenient, there is a function called `close`!

```C
close(fd);
```

Simplest one by far! With this function call we simply tell the operating system that we will no longer use the file descriptor. This step is optional, but just keep in mind that certain unix systems have a maximum of open file descriptors or can artificially limit the amount of opened file descriptors a process can have, so its always a good practice to close them when you're no longer using them.

### 4. File information
In contrast to the before mentioned functions, *stat* is actually a family of functions that basically implement the same things but using different parameters. For example:
- `stat` takes a path name and a pointer to the `stat` structure where information about the desired file is going to be stored.
- `fstat` takes a file descriptor and a pointer to the `stat` structure.

There is also `lstat`, that checks if the given pathname is a symbolic link, and if it is it simply returns information about the link instead of the file the link refers to.

In our case we'll use the `fstat` function as we already will have an open file descriptor that we can use.
## We have the tools, lets implement the command now
The typical use case for `cat` is simply reading the files passed from the command line and simply printing them to standard output. For this, the utility needs to go through the command line arguments and apply the before mentioned process of opening, reading/writing and closing the file.

Where do we take the command line arguments? Have you ever wondered what those `argc` and `argv` parameters are in the main function? They are actually the argument count (`argc`) and the actual arguments(`argv`)! Knowing this, we can simply loop on the command line arguments and apply the before mentioned process:

```C
for (int i = 0; i < argc; i++) {
	int fd = open(filepath, 0, O_RDONLY);
	
	struct stat statbuf;
	fstat(fd, &statbuf);
	
	char *buf = malloc(statbuf.st_size);
	read(fd, buf, statbuf.st_size);
	write(STDOUT_FILENO, buf, rc);
	free(buf);
}
```
For the sake of simplicity I've removed all error checking so that its simpler to read and understand, but the full error checked version can be found on the [github repository](https://github.com/IkerGalardi/learn-posix/blob/main/cat.c).

The shown code simply follows the above scheme of `open` -> `read` -> `close` on the argument files and simply writes to standard output. Also uses `fstat` in order to allocate a buffer large enough to hold the file data.
## Finishing words
This article is just simply an introduction to concepts and basic functions for reading and writing to file descriptors. If more information is needed like more ways to open files or write to them simply check the manual pages provided by your Linux/BSD. For example, there are several ways to open files but we simply used the simplest one, for checking more ways simply `man 2 open`.

Manual pages are a really good resource to learn about all the details that many tutorials and classes skip over for the sake of simplicity. These manuals normally include a group of functions (in the case of the `open` manual we can find the definition of `open`, `creat` and `openat`), explanation for all the parameters and struct fields, return values and error handling, and the most interesting one for learning purposes, a *see also* section with related functions.

You can find my implementation on my [learn-posix](https://github.com/IkerGalardi/learn-posix) where I also will add implementation for other posix utilities discussed on future articles.
