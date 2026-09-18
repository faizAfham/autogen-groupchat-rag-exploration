# AutoGen GroupChat

AutoGen's `GroupChat` lets multiple conversable agents share a single conversation
thread. A `GroupChatManager` selects the next speaker each round, either with an
LLM ("auto"), round robin, a fixed order, or a custom function. Speaker order can
be constrained with `allowed_or_disallowed_speaker_transitions` to enforce a
deterministic pipeline instead of letting the manager's LLM pick freely.

# Retrieval-Augmented Generation in AutoGen

`RetrieveUserProxyAgent` (in `autogen.agentchat.contrib`) adds RAG to an agent: it
chunks local documents, embeds them (Chroma's default sentence-transformer
embedding unless overridden), stores them in a Chroma collection, and retrieves
the top-k chunks most similar to a query. `generate_init_message(problem, n_results)`
returns the retrieved context concatenated with the original question, which is
the standard way to ground a conversation's opening message in retrieved evidence.

# Why Role-Based Multi-Agent Pipelines Reduce Hallucination

Splitting a single "answer the question" agent into a planner, a retriever, and a
responder narrows each agent's job:
- The planner only decides what to search for, so it cannot fabricate an answer.
- The retriever only returns evidence it actually found, so it cannot invent facts.
- The responder is instructed to answer strictly from the retrieved evidence and
  say "I don't know" when the evidence doesn't cover the question, rather than
  filling gaps from parametric memory.

This narrows each LLM call's task, which tends to reduce hallucination compared to
a single agent that must plan, search, and answer in one pass.

# Latency Trade-offs in Multi-Agent Pipelines

Each additional agent turn adds at least one LLM round trip. A 3-agent pipeline
(planner, retriever, responder) is slower per query than a single-agent RAG
answer, but retrieval itself is cheap relative to LLM generation: vector search
over a small local Chroma collection typically completes in tens of
milliseconds, while each LLM call can take seconds. The dominant latency cost is
the number of LLM-backed turns, not the retrieval step.

# Scaling Multi-Agent Workflows in Production

Extension points for scaling this pattern beyond a demo:
- Cache retrieval results for repeated or similar queries to skip re-embedding.
- Run retrieval concurrently with planning when the plan doesn't depend on
  retrieved content, instead of a strict sequential pipeline.
- Move the vector store from local Chroma to a managed/shared vector database
  so multiple agent instances can share one index.
- Add a max-round and cost budget per conversation to bound worst-case latency
  and spend before it reaches production traffic.
- Stream partial responses from the responder agent to cut perceived latency.
