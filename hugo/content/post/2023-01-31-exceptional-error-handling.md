---
title: Non exceptional error handling and C++
date: 2023-01-30
draft: true
tags: ["experiment", "C++"]
---

For the longest time, error handling while programming has been a pain in the ass. Weird and inconsistent ways to detect errors on APIs, global variables to see what actually happened (looking at you, `errno`), treating errors as exceptional code paths that make it difficult to handle... you name it. What do you get with this? Confusion, a lot of confusion.

Error handling should be a very important part of software development, as many can expect, everything (trust me, absolutely everything) can go wrong. Thus, a programmer can expect that error handling is easy and noticable. Ignoring a possible error should be explicit, making it easy to spot possible points of failure. A small [talk by Jason Turner](https://www.youtube.com/watch?v=zL-vn_pGGgY) illustrates how important it is to do so when designing an API.

Let's start our journey on the error handling mechanisms with C. In C, the main error handling mechanism is using `errno`... What is `errno` you might ask. Well, `errno` is a global variable to represent a possible error. Let's take the `open` function's man page:

```
    On success, open(), openat(), and creat() return the new file descriptor 
    (a nonnegative integer). On error, -1 is returned and errno is set to indicate 
    the error.
```

Let's employ what the man page says, to be as correct as possible when using the `open` function:

```C++
    int fd = open("super/cool/file", O_RDONLY);
    if(fd == -1)
    {
        switch(errno)
        {
            // Do error handling on specific error           
        }
    }

    // Do whatever with the file
```

Amazing, easy to use, impossible to miss... Yes, there are problems with the `errno` or `GetLastError` error handling scheme. What about just using the file descriptor without trying to check any error condition? Does the compiler atleast warn us about that? No, and thats a **BIG** problem, as the API can be misused without even knowing you are doing something wrong. Come on, we have flying machines and hot showers, we can do better than this!

Indeed, we can do better. What is the next step on improving error handling? Exceptions. Exceptions work by specifying a `try` block where you program the happy path (as if everything is okay), and a `catch` block where you catch the actual error:

```java
    try {
        File file = new File("filename.txt");
        // Do whatever with the file
        myReader.close();
    } catch (SpecificException e) {
        // Do error handling on specific error or propagate upwards
    }
```

Failing to create the `File` object the execution of the `try` block stops, and starts executing the `catch` block with information about what happened. This construct lets programmers divide error handling from the algorithm itself and making much more clear what the intent is. Apart from that, as a programmer you can decide to not handle the error in that specific place, and let it bubble up. Building error handling into the language also has the advantage of forcing you to handle it somewhere, which for distracted people like myself, can be a great help.

Still, this is not the perfect solution either. The word exception itself makes it clear... error handling is not about handling the special case rarely found, errors happen all the time, and the application must be prepared to handle it. Having specific exceptions per error case can also be a pain to deal with, as the code can be cluttered up with `catch` blocks. And personally, I don't find it very elegant to suddenly stop the flow of execution.

So... whats next? Is there something better? Of course, and rust does it of course, rust is perfect. Rust uses the the convination of its strong type system and generics in order to make error enforced and while maintaining the flow of execution. By adding the pattern matching mechanisms to this, you can do error handling in a very ergonomic way. Let's take a look at an example from the rust documentation about number parsing:

```rust
    let number_str = "10";
    let number = match number_str.parse::<i32>() {
        Ok(number)  => number,
        Err(e) => {
            // Do error handling or propagate upwards
        },
    };

    // Do whatever with the number
```

isn't it beautiful? This approach takes the advantages of both approaches by forcing you to handle the error while maintaining the control flow, leading to much cleaner and safer code (in my opinion at least). In addition to this, there is a `?` operation that lets the error bubble up without much hassle where the same error type is returned.

This is all well and good, but what happens with my old non-rust codebase? Can I benefit from this new way of handling errors in my C/C++ code? Well, if the code is only C, you're out of luck as there is nothing like generics. If you're using C++ I am coming to the rescue 😉.

To mimic this type of error handling we're going to take advantage of a [small library](https://github.com/TartanLlama/expected/) that tries to comply with the hopefully future new type called [`std::expected`](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0323r3.pdf) which shamelessly copies rust's `Result`. With that, and the help of a next small macro we will explore if we can bring the joy of error handling from rust to our beloved C++.

```C++
    #define TRY(x)                                          \
            ({                                              \
                auto __error_or_correct = (x);              \
                if(!__error_or_correct.has_value())         \
                    return __error_or_correct.error();      \
                __error_or_correct.value();                 \
            })
```

This macro takes the advantage of the [compound statements](https://gcc.gnu.org/onlinedocs/gcc-8.1.0/gcc/Statement-Exprs.html#Statement-Exprs) extension in order to immitate the `?` operator from rust. Let's put this in practice... Using the `tl::expected` object, let's implement a posix `open` function:

```C++
    tl::expected<int, errno_t> open(const char* path, int flags, mode_t mode)
    {
        int fd = open(path, flags, mode);
        if(fd == -1)
        {
            return tl::make_unexpected(errno);
        }

        return tl::make_expected(fd);
    }
```

Cool, simple to make, right? What advantages does this have over the traditional way? Not handling the error becomes explicit, making the API harder to use wrongly. Now lets create a function that takes in a path and reads the entire file using the wrapper function we just created:

```C++
    tl::expected<std::string, errno_t> read_entire_file(const char* path)
    {
        auto fd_or_error = open(path, 0, O_RDONLY);
        if(!fd_or_error.has_value())
        {
            return tl::make_unexpected(fd_or_error.error());
        }

        auto fd = fd_or_error.value();

        // Do the actual reading of the file...
    }
```

Error handling is explicit, cool right? Well, checking manually if there is an error and trying to bubble up the error explicitly is cumbersome, only if there was a macro called `TRY` that could remove writing the same check and bubble up code every time the same error type is returned... Right, there is such macro! Lets put it in practice:

```C++
    tl::expected<std::string, errno_t> read_entire_file(const char* path)
    {
        auto fd = TRY(open(path, 0, O_RDONLY));

        // Do the actual reading of the file...
    }
```

Amazing, the code is so concise, and still, you cannot miss error as with the original posix API. Isn't this *perfect*? It is in this simple case, but what happens in the case of having a different error type? The `TRY` macro cannot help us as the type system probably won't know how to convert one error type to another, leaving us the same error handling as without the macro. I have a small solution that I have not tested but seems actually cool... Errors could be implemented by using `enum class`-es, making it even harder to missinterpret the actual error value, and this could give us the advantage of creating an operator overload of the casting between one error enum to another, potentially making it completely transparent; but as I said, I have not really tested the solution, so I could be completely wrong.

I really like how this small error handling experiment turned out, I really think this could be useful, and even more useful when `std::expected` becomes an actual thing in the standard. A big advocate for this type of error handling in C++ is the [SerenityOS project](https://serenityos.org/), which I half copied the implementation of the `TRY` macro from. 

This is all I wanted to talk about for now, there will be probably another follow up post after some time using this error handling mechanism giving more in depth analysis and how viable it is to actually implement and use so stay tuned. Bye!