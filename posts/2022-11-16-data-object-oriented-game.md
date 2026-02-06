---
title: Data or object oriented? That is the question
date: 2022-11-04
draft: false
tags: ["paradigm", "gamedev", "project"]
---

# Data or object oriented? That is the question

Let me tell you the story of how object oriented programming is not always the way to go. Unless you studied computer science on the 90s, every school, university or bootcamp tries to convince students that object oriented programming is **THE BEST** and how functional or procedural programming is for old people (I certainly felt that at university).

Well oh well, data oriented programming is the new kid in town, so what gives? That's a question I've tried to evade for a while until I started my new game project. Let's start from the beginning... What is object oriented programming?

## Object oriented programming 

Object oriented programming is a paradigm based on objects, which contain data and code to modify that data. Convining data and code into objects lets programmers abstract away complex concepts, and thus, simplifying development. That's the theory told by experts and random webpages, is that real? Let me tell you the story of how game development lead me to obsess with clean design and design patters.

A couple of months ago I started a remake of an old gameboy game I like a lot and for which sprites are (not legally) available. So I said, why not try to recreate and try to learn a few things along the way like `cmake` and post processing using OpenGL. At the moment, I already was a bit obsesed with software architecture and clean design, so what about playing god and trying to plan all the game software architecture from the start.

There comes the big error that even professional software developers have, over engineering and over abstracting. Abstractions and encapsulation do actually help build more complex, but do you know what happens when you over engineer and over abstract? Noise, a lot of noise. That makes the project difficult to read and maintain.

During the preparantion process a recapitulation of all the features was made, and with that and drawio I started to plan all the classes, libraries and design decisions. What did that lead to? 5 libraries that could easily be included in just one (or even none, who needs libraries?), inheritance because *"maybe in the future we could have multiple of these"*... Currently, as I'm writing this post, the engine is a bit of a mess that needs to be solved before even continuing (I'm ashamed to admit this, refactoring on a 2 months old project just because I wanted to feel smart at the start).

Still, what I've mentioned untill now is only my fault; What did object oriented programming do in all these shenanigans? Well, let me share with you a [talk about rust game development which focuses](https://www.youtube.com/watch?v=aKLntZcp27M) which will better explain how object oriented programming can help your game code be a pain and how to solve it with data oriented programming.

## Yet another perfect solution, but actually yes this time and situation
What a title! Yes, I feel this solution actually will hold on until I consider the project. Applying data oriented design into games turns out to have another name: entity component system. Entities hold components, components hold data, and systems modify and do things with that data.

With that simple design, we can define scenes easily like a collection of entities. With this simple design, we can also add functionality really simply by adding new systems. That's it! Let's look at a simple example on how rendering works currently:

```C++
const auto& registry = m_world_manager.registry();
const auto& view = registry.view<Transform, Sprite>();
for(const auto& entity : view)
{
    const auto& transform = registry.get<Transform>(entity);
    const auto& sprite = registry.get<Sprite>(entity);
    
    m_renderer.render_texture_quad(transform.position,
                                   sprite.texture);
}
```

Adding new systems becomes as easy as adding similar pieces of code but with the specific components needed for that system.

## Conclusions

Not much more to say, I'm in the honeymoon phase with this. Soon I'll open source the engine and game code, but still, I need to sort out some issues like refactoring and supporting windows so that more people can see and play the game.
