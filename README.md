# Multi-Agent Group Chat with Retrieval-Augmented Generation (AutoGen)

This repository explores and implements a multi-agent conversational system using
Microsoft AutoGen, combining GroupChat orchestration with Retrieval-Augmented Generation (RAG).

## What this project demonstrates
- Multi-agent collaboration using role-based agents
- Retrieval-augmented generation for grounding responses in external documents
- GroupChat orchestration for coordinated reasoning across agents

## Source & Reference
This implementation is based on the official Microsoft AutoGen example:
https://microsoft.github.io/autogen/0.2/docs/notebooks/agentchat_groupchat_RAG/

The goal of this repository is **learning, experimentation, and extension**, not original authorship of the AutoGen framework.

## My Contributions
- Understood and adapted the GroupChat + RAG architecture
- Ran experiments with document retrieval and agent roles
- Documented system behavior, limitations, and extension points
- Prepared the system as a reusable template for future multi-agent workflows

## Tech Stack
- Python 3.8+
- Microsoft AutoGen
- LangChain (for RAG)
- OpenAI API / Claude API

## Setup
```bash
pip install pyautogen langchain openai
```

## Usage
See `main.py` for implementation details.
