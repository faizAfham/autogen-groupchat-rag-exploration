# Project Overview

**Goal:** Build the implementation behind this resume bullet —
"Multi-Agent RAG System using AutoGen (March 2024) — GroupChat + RAG,
planner/retriever/responder roles, hallucination reduction, latency/scaling
analysis" — as the linked GitHub repo, `faizAfham/autogen-groupchat-rag-exploration`.

**State:** Implementation, tests, README, and analysis write-up are done and
validated (`python test_agents.py` passes against pinned `pyautogen==0.2.25`
in a scratch venv). See [[architecture]] for how the pieces fit together. Not
yet run end-to-end with a real LLM (user hasn't added an API key yet), so
`analysis/notes.md` has two latency rows still marked pending.

**Key constraint:** No specific LLM provider chosen — user said they'll add
"some free LLM model API" later. `config.py` is provider-agnostic (any
OpenAI-API-compatible endpoint) so that choice doesn't require code changes.

**Next step:** User adds `OPENAI_API_KEY` (+ `OPENAI_MODEL`/`OPENAI_BASE_URL`
if not plain OpenAI) to `.env`, runs `python main.py`, and the two pending
latency numbers in `analysis/notes.md` get filled in from that real run.
Commit/push has not happened yet — gated on user request per session rules.

**Where to look:**
- `README.md` — architecture, setup, usage.
- `analysis/notes.md` — the actual "analysis" the resume bullet claims.
- `progress.md` / `SESSION_HANDOFF.md` — session-to-session continuity.
