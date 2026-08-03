---
title: I set the wrong question for the model
date: 2026-08-03
description: I asked four setups for the research ideas most likely to be accepted. They converged on the same two, and the reason was in my question, not in the models.
status: budding
---

I'm a clinician and I do medical LLM research. One day I got curious and handed the research idea itself to the models. Not the method. What to study.

Here is the prompt I used:

> "You are a medical LLM researcher writing a research proposal, but you don't even have a research idea. The humans available to you are a physician with 5+ years of pediatric clinical experience and an LLM researcher. You have nearly unlimited sessions and compute. If you were building a research idea aimed at submission to [journal], give me the 5 ideas **most likely to be accepted**."

I ran it in four places.

| run | setup | model | local context |
|---|---|---|---|
| A | Claude Code, my own harness | Opus 5 | files, memory, working rules all open |
| B | Claude Code | Opus 5 | blocked in the prompt |
| C | claude.ai app | Opus 5 (high) | none |
| D | ChatGPT | 5.6 sol pro | none |

Different models, different tool access, different limits on answer length. I thought I had spread the conditions pretty far apart.

Twenty ideas came back, and when I looked at what each answer had put at the top they were not twenty different ideas.

## They converged on two

All four answers contained the same two kinds of task. C and D put the same two in first and second place.

What caught my eye was not the topics. It was what those two tasks had in common.

- an official guideline exists, so the right answer can be made deterministic
- synthetic data can be generated without limit
- scoring is automatic, no human raters needed
- no IRB burden
- results come out as clean numbers
- easy to tie to clinical harm

These are not the properties of a good research question. **They are the properties that lower the odds of rejection.** A guideline means no fight over the gold standard. Automatic scoring removes the bottleneck of recruiting raters. No IRB means a fast start. Clean numbers make the method hard to attack. Each one erases a reason to say no.

The models did exactly what I told them to do. I thought this was a model comparison. It wasn't. **It was a test of what I had asked for.**

## The conditions were far apart, so why did they converge?

This was the strangest part. Different tool access, different context, different companies. Why the same place?

If four independent systems land on the same answer, that supports the answer. Here I think it reads the other way. Converging across that much spread means **the difference the environment makes is smaller than the difference my ask makes.** The things I treated as independent variables didn't behave like independent variables.

And the four priors were never independent. The sense of what a good medical AI study looks like comes from the same literature, the same reviewer complaints, the same methods textbooks. These weren't four different models. They were four compressions of the same corpus.

## All four went local

There was a second convergence, and all four hung their novelty on the same peg: this is our country's data, our country's guideline, so it's different.

I'll be honest: I hate seeing this come out of brainstorming. Koreans write papers in English and present in English. You don't have to be a native speaker to get credit for an English paper and English prompting. Carving out a spot for myself through locality is not what I want to do.

This experiment made me understand why it happens. Locality is the cheapest way to answer "why is this new?" Build novelty into the method and you get an argument about the gold standard, a heavier rubric, more human hours. Locality fills the novelty box and pays none of that.

The models weren't fixated on locality. Tell something to minimize its chance of rejection and locality is the cheapest thing on the shelf.

## Only the absence claims were wrong

One more thing fell out of it. Run A, the one inside my own harness, put a strict rule on the literature collection step. Don't mix what the source said with what you inferred. Attach the raw output to every claim. If you can't attach it, write that you couldn't check it.

It held during collection. It broke in the final summary. Sentences like "no such study exists yet" and "this one is the surest bet" came out far stronger than the evidence under them, and for some of them the study already existed.

There was a pattern to it. **Everything that was wrong was a claim that something didn't exist.** Confirming that a thing exists and confirming that it doesn't are completely different jobs, but once they become a line in a summary they are both one sentence. The rule I put on collection was never put on the conclusion.

## What I actually learned

From here it's about me, not the models.

I was in a hurry about output. So I pushed getting published into the prompt. And the models reflected that straight back at me, toward the safest thing available. *The user* was anxious, and the models read that and optimized for it.

What did I actually want? To make something new, run it fast, check it, and see a result. But I kept that in my head and never put it in the input. What I put in was "most likely to be accepted."

**The model isn't the one publishing.** Getting published is a question of my own ability, and the model solves the thing I wrote down. Write down the wrong thing and a correct answer comes back. What I got wasn't a wrong answer. It was an exact answer, and the problem was in the question I set. What I asked for was not what I wanted.

Next time I won't ask for one thing. The safest bet for getting published. The biggest contribution that two people can still actually run. The one with a low chance of success that could open a field. Whether asking for all three separately breaks the convergence, or whether the third one lands in the same place anyway, is what I want to know now.
