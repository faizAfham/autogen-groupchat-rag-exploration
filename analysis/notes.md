# System Behavior, Latency Trade-offs, and Extension Points

Companion to `README.md`'s architecture section. Written against the
Planner -> Retriever -> Responder pipeline in `agents.py`.

## System Behavior

- **Deterministic role order.** `allowed_or_disallowed_speaker_transitions`
  pins the turn order to `User -> Planner -> Retriever -> Responder -> User`.
  This trades away AutoGen's LLM-driven `"auto"` speaker selection (used in
  the official `agentchat_groupchat_RAG` example) for predictability — no risk
  of the manager picking Responder before retrieval has happened, or looping
  back to Planner unexpectedly.
- **Retriever never calls an LLM.** Its group-chat reply is a direct call to
  `generate_init_message()` (Chroma similarity search + formatting), registered
  via `register_reply` at `position=0`. It only ever returns evidence that was
  actually found in `data/knowledge_base/` — it cannot fabricate content, which
  is the main hallucination-reduction lever in this design (the LLM agents
  never see the raw question without also seeing what was or wasn't retrieved).
- **Responder is constrained, not just prompted.** Its system message requires
  it to say "I don't know based on the retrieved documents" when the context
  doesn't cover the question, rather than filling gaps from parametric
  knowledge. This is a prompting-level guardrail, not an architectural one —
  it can still fail if the model ignores the instruction, which is a known
  limitation of instruction-only grounding (see Extension Points).

## Latency Trade-offs

Retrieval-only latency, measured directly against the 1-doc knowledge base
(Chroma + default `all-MiniLM-L6-v2` sentence-transformer embeddings), on a
2024 MacBook Pro, CPU only, no GPU:

- **Cold** (first call: loads the embedding model, creates the Chroma collection): ~1-3s, one-time cost per process.
- **Warm** (subsequent queries, model already loaded): **~12ms average** over 3 distinct queries (0.0122s, 0.0116s, 0.0119s).

<!-- ponytail: fill in the two LLM-turn rows below after running
`python main.py` with a real API key. -->

| Agent | What it does | Calls an LLM? | Observed latency |
|---|---|---|---|
| Planner | question -> search query | yes | _pending: run `python main.py` with a real key_ |
| Retriever | vector search only | no | ~12ms warm (measured above) |
| Responder | context -> grounded answer | yes | _pending: run `python main.py` with a real key_ |

Directionally, this matches the general pattern documented in
`data/knowledge_base/autogen_overview.md`: local vector search over a small
Chroma collection is on the order of tens of milliseconds once the embedding
model is warm, while each LLM call is on the order of seconds. In this
pipeline that means **2 of the 3 agent turns (Planner, Responder) dominate
end-to-end latency**, not retrieval — adding more retrieval sophistication
(re-ranking, hybrid search, more chunks) is nearly free relative to adding
another LLM-backed turn.

Practical consequence: if the pipeline needs to scale down latency, the
highest-leverage change is reducing LLM turns (e.g. merging Planner into the
Responder's prompt for simple questions) or running independent LLM turns
concurrently, not optimizing the retriever.

## Extension Points for Production

- **Skip the Planner for simple questions.** A cheap heuristic or a small/fast
  model call can decide whether the raw question is specific enough to search
  directly, cutting one LLM turn off the common case.
- **Cache retrieval results** keyed on the (normalized) search query to avoid
  re-embedding repeated or near-duplicate questions.
- **Move Chroma to a shared/managed vector store** once more than one process
  or instance needs the same index — the current setup assumes a single local
  collection.
- **Bound cost and latency per conversation** with `max_round` (already set to
  6) plus a token/cost budget, so a misbehaving loop can't run away in
  production traffic.
- **Verify groundedness, don't just prompt for it.** The Responder's "answer
  only from context" instruction is not enforced in code. A production version
  would add a check (e.g. a lightweight classifier or a second LLM call) that
  flags answers not attributable to the retrieved chunks, since prompting
  alone is known to be an imperfect hallucination guardrail.
- **Stream the Responder's output** to the caller instead of waiting for the
  full GroupChat to terminate, since the Responder's turn is the largest
  single latency contributor.
