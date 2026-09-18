# Progress

## Completed
- Linked local directory to existing GitHub repo `faizAfham/autogen-groupchat-rag-exploration` (had only a README).
- Implemented Planner -> Retriever -> Responder pipeline on `pyautogen[retrievechat]`
  (`agents.py`, `config.py`, `main.py`), with deterministic speaker order via
  `allowed_or_disallowed_speaker_transitions`.
- Added a 6-doc local knowledge base (`data/knowledge_base/`) covering AutoGen
  GroupChat/RAG internals, used as both the RAG corpus and the source material
  for the analysis write-up.
- Added `test_agents.py`: latency-aggregation unit test + a retrieval test that
  needs no LLM API key.
- Revised `README.md` with the real architecture, setup, usage, and test instructions.

## Current
- Validated against the real installed library: `pip install pyautogen[retrievechat]`
  defaults to `autogen` 0.9.0 (the AG2 fork's new API), which is NOT
  API-compatible with this code. Pinned `requirements.txt` to
  `pyautogen[retrievechat]>=0.2.25,<0.3` (the classic "March 2024"-era API)
  and verified real signatures in a scratch venv (`/tmp/autogen_probe_venv`).
- Found and fixed a bug: `RetrieveUserProxyAgent.generate_init_message()` is
  just the base carryover handler in 0.2.25, not the retrieval trigger.
  Retrieval is actually triggered via the static `message_generator(sender,
  recipient, context)` method. Fixed in `agents.py` and `test_agents.py`.
- `python test_agents.py` passes against pinned pyautogen 0.2.25 (exit code 0):
  latency aggregation math is correct, and retrieval surfaces the relevant
  chunk for a sample question with no LLM/API key involved.
- Measured real warm retrieval latency (~12ms avg over 3 queries, CPU only)
  and filled it into `analysis/notes.md`.

## Remaining
- User adds a real (free-tier) OpenAI-compatible API key to `.env` and runs
  `python main.py` for an end-to-end transcript with real Planner/Responder
  LLM-turn latency numbers (the only two pending rows in `analysis/notes.md`).
- Decide whether to commit/push (not done yet — commits are user-gated).
- The user's actual machine doesn't have `pyautogen` installed yet — only the
  scratch venv at `/tmp/autogen_probe_venv` does. User needs to
  `pip install -r requirements.txt` (ideally in their own venv) before running
  `main.py`/`test_agents.py` themselves.
