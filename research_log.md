# Research Log (append-only)

## 2026-09-18
- Confirmed via `gh api` that `faizAfham/autogen-groupchat-rag-exploration` already
  existed on GitHub with 2 commits (initial commit + a README-only revision),
  no implementation code. Local directory was empty — no prior local clone.
- Decision: clone the existing remote into place (preserve git history/README)
  rather than starting a fresh repo, so this session's work extends rather than
  replaces what's already there.
- Decision: match the README's stated reference (official AutoGen 0.2
  `agentchat_groupchat_RAG` notebook) but replace the notebook's Boss/Coder/PM
  roles with Planner/Retriever/Responder to match the target resume bullet's
  wording exactly.
- Decision: use `allowed_or_disallowed_speaker_transitions` for a deterministic
  pipeline instead of the LLM-driven `"auto"` speaker selector used in the
  official example — more reliable for a portfolio demo, still a documented
  AutoGen 0.2.x feature (fits the "March 2024" framing).
- Decision: made the Retriever's group-chat turn a plain retrieval call
  (`generate_init_message`) with no LLM call of its own, via `register_reply`.
  This keeps retrieval latency cheap and isolated from LLM latency, which is
  the exact comparison the target resume bullet claims to have analyzed.
- User declined to pick a specific LLM provider up front ("will put in some
  free LLM model API later"); config (`config.py`) reads model/key/base_url
  from env vars so any OpenAI-API-compatible provider works without code changes.
- Discovery: `pip install pyautogen[retrievechat]` with no version pin resolves
  to 0.9.0 (the AG2 fork's rewritten API), not the classic 0.2.x API the
  official `agentchat_groupchat_RAG` notebook and this code target. Verified in
  a scratch venv that `pyautogen==0.2.25` is still installable from PyPI and
  matches the expected `GroupChat`/`RetrieveUserProxyAgent` signatures. Pinned
  `requirements.txt` to `>=0.2.25,<0.3` so `pip install -r requirements.txt`
  doesn't silently grab an incompatible major version.
- Bug found by inspecting real source: `generate_init_message()` on
  `RetrieveUserProxyAgent` in 0.2.25 is inherited from the base agent and only
  handles carryover text — it does NOT trigger retrieval. The actual retrieval
  entry point is the static method `RetrieveUserProxyAgent.message_generator(
  sender, recipient, context)`, which calls `retrieve_docs()` internally.
  Fixed `agents.py`'s `retrieve_only_reply` and `test_agents.py` to call that
  instead. Confirmed via `python test_agents.py` (exit code 0) against the
  pinned version.
- Measured warm retrieval latency directly: ~12ms average (3 queries, CPU,
  `all-MiniLM-L6-v2`), used in `analysis/notes.md`.
