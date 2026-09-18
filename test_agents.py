"""Self-checks with no LLM API key required: latency aggregation + retrieval quality."""
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

from agents import LatencyTracker, TurnLog, build_retriever


def test_latency_tracker_aggregates_per_speaker():
    tracker = LatencyTracker()
    tracker.turns = [
        TurnLog("Planner", 0.1),
        TurnLog("Planner", 0.3),
        TurnLog("Responder", 2.0),
    ]
    summary = tracker.summary()
    assert summary["Planner"] == {"turns": 2, "total_s": 0.4, "avg_s": 0.2}
    assert summary["Responder"] == {"turns": 1, "total_s": 2.0, "avg_s": 2.0}


def test_retriever_finds_relevant_chunk_without_any_llm_call():
    retriever = build_retriever("data/knowledge_base", model="unused-for-retrieval")
    context_message = RetrieveUserProxyAgent.message_generator(
        retriever, None, {"problem": "Why do multi-agent pipelines reduce hallucination?", "n_results": 3}
    )
    assert "hallucination" in context_message.lower()


if __name__ == "__main__":
    test_latency_tracker_aggregates_per_speaker()
    test_retriever_finds_relevant_chunk_without_any_llm_call()
    print("ok")
