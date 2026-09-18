# Architecture Summary

Pipeline: `User -> Planner -> Retriever -> Responder -> User`, enforced via
AutoGen `GroupChat(allowed_or_disallowed_speaker_transitions=...)`.

- `config.py` — builds an OpenAI-API-compatible `config_list` from env vars
  (`OPENAI_API_KEY`, `OPENAI_MODEL`, optional `OPENAI_BASE_URL`). No provider
  hardcoded; works with any OpenAI-compatible free-tier API.
- `agents.py` — `build_pipeline()` constructs the 4 agents + manager;
  `build_retriever()` wraps `RetrieveUserProxyAgent` with a `register_reply`
  override so its group-chat turn is pure vector search (no LLM call);
  `LatencyTracker` wraps `generate_reply` on each agent to time turns.
- `main.py` — entry point, runs one question through the pipeline, prints the
  transcript and a per-agent latency summary.
- `data/knowledge_base/` — local RAG corpus (currently one doc covering
  AutoGen GroupChat/RAG internals, hallucination reduction, latency, and
  scaling — doubles as demo content and background reading).
- `test_agents.py` — no-API-key self-check: latency aggregation math, and that
  retrieval actually surfaces the relevant chunk for a sample question.

See `analysis/notes.md` for the latency/hallucination/scaling findings this
architecture was built to support.
