"""Run one question through the Planner -> Retriever -> Responder pipeline."""
import sys

from agents import LatencyTracker, build_pipeline
from config import get_config_list

DOCS_PATH = "data/knowledge_base"
DEFAULT_QUESTION = "Why do role-based multi-agent pipelines reduce hallucination?"


def run(question: str) -> None:
    config_list = get_config_list()
    user_proxy, planner, retriever, responder, manager = build_pipeline(DOCS_PATH, config_list)

    tracker = LatencyTracker()
    for agent in (planner, retriever, responder):
        tracker.wrap(agent)

    user_proxy.initiate_chat(manager, message=question)

    print("\n--- Latency summary (seconds per agent turn) ---")
    for name, stats in tracker.summary().items():
        print(f"{name}: {stats}")


if __name__ == "__main__":
    run(" ".join(sys.argv[1:]) or DEFAULT_QUESTION)
