---
title: Data or object oriented?
date: 2022-11-04
draft: true
tags: ["paradigm", "gamedev", "project"]
---

Let me tell you the story of how object oriented programming is not always the way to go. Unless you studied computer science on the 90s, every school, university or bootcamp tries to convince students that object oriented programming is **THE BEST** and how functional or procedural programming is for old people (I certainly felt that at university).

But, first of all, what even is object oriented programming?

## Object oriented programming
Let's start from the beginning, how did people program in the beginning of times? They programmed in assembly. What is assembly? you might ask. Well, to better understand it, lets write some ficticious assembly in order to calculate the length of a three dimensional vector:

```
    // Load data into registers
    ld f1, X
    ld f2, Y
    ld f3, Z

    // X²
    mul f1, f1, f1

    // Y²
    mul f2, f2, f2

    // Z²
    mul f3, f3, f3

    // sqrt(X² + Y² + Z²)
    add f1, f1, f2
    add f1, f1, f3
    srqt f1, f1

    // Store the result
    st LENGTH, f1
```

Do you find this piece of assembly code readable or expressive? No, you are not alone, no one thinks this is *the future* of programming because the code you produce is maintainable and readable. This code does not even have control flow instructions, which makes the code even more spaghetti like.

Still, this kinds of instructions are what actual CPUs understand, so some clever people thought... what if we write code on a more understandable language, and we *compile* it to assembly (or machine language to be more exact)? There C like simple languages where born. Lets take a look on how that code could be written in C:

```C
float length(float x, float y, float z)
{
    return sqrt(x*x + y*y + z*z);
}
```

Isn't that gorgeous? The code suddenly is readable. These programming languages did not only add much more expressiveness to the written code, but also brought concepts like functions (reusable pieces of code) and structures (pack of easily accessible data). Not saying that those features could not be used in assembly, they could be used, but accessing structure data needed to be done manually, as with functions, which made them a bit cumbersome to use.

Still, some programmers felt that just grouping code and data was not enough, and the concept of objects began to arise. Objects (or classes) basically group data and operations to that data. Again, these features could be accessed from C-like low level languages, but syntactic sugar to automate these kinds of things help programmers focus on the actual algorithms instead.

What did this lead to? More constructs to help abstraction. What about objects with same functionality and same data? Well, we can define an interface and make implementations for different use cases. What about having a base class that implements some things, and then inherit that functionality in a more complex class, but treating it like a the base class? Well, there you have it, polymorphism. Is it a good idea to expose all the data to the world? Not ofcourse, what if we accidentally touch something we don't want? Lets encapsulate the data then using getters and setters. This is basically object oriented programming. These constructs help abstract things away from the programmer, making in theory, easier to develop more complex software.

Everything is great now, right? Well, not really. Some kinds of applications can take benefit of this design patters, but others like game design not. Let me explain why...

## Introduction to game development (without an engine)

Games basically take input from the user, do whatever the game needs to do with that input, and then draw what is going on in the screen. That is achieved using an event loop. What does that look like?

```C++
    while(receive_input())
    {
        switch(input)
        {
            case key_down: player.move();
            case mouse_move: camera.move();
            ...
        }

        player.non_input_related_stuff();
        camera.non_input_related_stuff();
    }
```

That is a very simplified way of seeing an event loop. But that code has a problem: a hard dependency between the event loop and each entity that wants do something. Lets put into practice that fresh object oriented designby creating a game thing with common functions and implement specific functionality in another part to break the direct dependency between the game loop and each individual game thing.

```C++
    array<GameThing> things;
    while(receive_input())
    {
        switch(input)
        {
            case key_down: 
                for(thing : thigns)
                    thing.on_key_down();
            case mouse_move:
                for(thing : thigns)
                    thing.on_mouse_move();
            ...
        }

        for(thing : thigns)
            thing.on_update();
        
    }
```

Well, in the ideal world every GameThing would live in its own island so that no more hard dependencies can happen. But, our game has a health system to see if the player is dead or not and apply damage; the camera wants to follow the player, so player position needs to be accessible via a getter; the renderer needs to access player sprites so it can draw something into the screen, so another getter for that... Suddenly, the hard dependencies start appearing again, and suddenly the player class is huge with all the getters, setters and actual variables 🫤. [This](https://www.youtube.com/watch?v=aKLntZcp27M) talk speaks about these issues in more detail.

## What is the solution?
Here comes data oriented programming and entity component systems. Entity component systems basically take data oriented programming and applies it to game development by dividing each module of a game into three categories: entities, groups of components; components, group of data; systems, functionality applied to entities and its components.

Using these design pattern we can create a health component that the damage and health system will modify and use, we can also create a sprite and position components so that the renderer know what and where to draw... Great! The only hard dependencies are the actual data that each system needs!

Apart from that, using ECS can lead to better performance, as the data can be more easily packed in memory to improve data locality, and make use of those sweet sweet cache memory more efficiently; locks can be more easily be placed so that the code can be parallelized with much less contention...

## Conclusions

Start testing ECS now! Fast! Not only games can benefit from this, so go check out if your specific use case can benefit from this. ECS systems are already available for several languages in libraries ([entt](https://github.com/skypjack/entt) on C++, [ecs](https://docs.rs/ecs/latest/ecs/) on rust...)

For me, I had to learn this design pattern the hard way... By suffering with object oriented programming and refactoring all that functionality into ECS by using [entt](https://github.com/skypjack/entt).
