# Single vs Multi-Agent System

A Python-based project demonstrating how a task can be solved using both a **Single-Agent System** and a **Multi-Agent System**, with a comparison of their LLM calls and token usage.

## Overview

This project explores two different approaches to building AI agents.

### Single-Agent System

A single LLM has access to both tools:

- Web Search
- Python Calculator

The LLM decides which tool to use, when to use it, and how many times to use it before producing the final answer.

```text
User Question
      ↓
    LLM
   ↙   ↘
Search  Calculator
   ↘   ↙
 Final Answer
