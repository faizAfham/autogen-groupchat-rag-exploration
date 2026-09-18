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

## Architecture
Three role-based agents run in a fixed pipeline inside an AutoGen `GroupChat`:
`User -> Planner -> Retriever -> Responder -> User`.
- **Planner** turns the user's question into a focused search query (no answering).
- **Retriever** (`RetrieveUserProxyAgent` + Chroma) looks up that query against
  `data/knowledge_base/` and returns the raw retrieved context — no LLM call.
- **Responder** answers strictly from that context, or says it doesn't know,
  and ends the conversation with `TERMINATE`.

Speaker order is enforced with `allowed_or_disallowed_speaker_transitions`
rather than the LLM-driven `"auto"` selector, so the pipeline is deterministic.
Each agent's turn is timed (`agents.py::LatencyTracker`) to compare retrieval
latency against LLM-generation latency. See `analysis/notes.md` for findings.

## Tech Stack
- Python 3.9+
- `pyautogen[retrievechat]` (GroupChat + RetrieveUserProxyAgent + Chroma)
- Any OpenAI-API-compatible LLM (OpenAI, Groq, Together, OpenRouter, Ollama, ...)

## Setup
```bash
pip install -r requirements.txt
cp .env.example .env   # fill in OPENAI_API_KEY (+ OPENAI_MODEL / OPENAI_BASE_URL for non-OpenAI providers)
export $(cat .env | xargs)
```

## Usage
```bash
python main.py "Why do role-based multi-agent pipelines reduce hallucination?"
```
Runs the pipeline once and prints the transcript plus a per-agent latency summary.

## Tests
```bash
python test_agents.py
```
No LLM API key needed — checks latency aggregation and that retrieval finds
relevant chunks in the local knowledge base.
