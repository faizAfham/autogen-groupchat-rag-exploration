"""Planner -> Retriever -> Responder GroupChat pipeline, with per-turn latency tracking."""
import time
from dataclasses import dataclass, field

import autogen
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

PLANNER_SYSTEM_MESSAGE = """You are Planner in a retrieval-augmented QA pipeline.
Given the user's question, output ONLY a short, specific search query (a few
keywords or a restated question) that the Retriever should look up. Do not
answer the question yourself and do not add commentary."""

RESPONDER_SYSTEM_MESSAGE = """You are Responder in a retrieval-augmented QA pipeline.
You will see the user's question and a CONTEXT block of retrieved document
excerpts. Answer strictly using facts present in CONTEXT. If CONTEXT does not
contain the answer, say "I don't know based on the retrieved documents" instead
of guessing. Cite which excerpt you used when possible. End your reply with the
word TERMINATE on its own line."""


@dataclass
class TurnLog:
    speaker: str
    seconds: float


class LatencyTracker:
    """Wraps agents' generate_reply to record per-turn wall-clock time."""

    def __init__(self):
        self.turns: list[TurnLog] = []

    def wrap(self, agent):
        original = agent.generate_reply

        def timed(*args, **kwargs):
            start = time.perf_counter()
            reply = original(*args, **kwargs)
            self.turns.append(TurnLog(agent.name, time.perf_counter() - start))
            return reply

        agent.generate_reply = timed
        return agent

    def summary(self) -> dict:
        by_speaker: dict[str, list[float]] = {}
        for t in self.turns:
            by_speaker.setdefault(t.speaker, []).append(t.seconds)
        return {
            name: {
                "turns": len(secs),
                "total_s": round(sum(secs), 3),
                "avg_s": round(sum(secs) / len(secs), 3),
            }
            for name, secs in by_speaker.items()
        }


def build_retriever(docs_path: str, model: str) -> RetrieveUserProxyAgent:
    """Retriever agent: answers with retrieved context only, no LLM call of its own."""
    retriever = RetrieveUserProxyAgent(
        name="Retriever",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        description="Looks up the Planner's search query against the local knowledge base "
        "and replies with the raw retrieved context. Speaks right after Planner.",
        retrieve_config={
            "task": "qa",
            "docs_path": docs_path,
            "chunk_token_size": 400,
            "model": model,
            "collection_name": "autogen_groupchat_rag_demo",
            "get_or_create": True,
        },
        code_execution_config=False,
    )

    def retrieve_only_reply(recipient, messages=None, sender=None, config=None):
        query = messages[-1]["content"]
        context_message = RetrieveUserProxyAgent.message_generator(
            recipient, sender, {"problem": query, "n_results": 5}
        )
        return True, context_message

    retriever.register_reply(autogen.Agent, retrieve_only_reply, position=0)
    return retriever


def build_pipeline(docs_path: str, config_list: list[dict]):
    """Returns (user_proxy, planner, retriever, responder, groupchat_manager)."""
    llm_config = {"config_list": config_list, "temperature": 0}

    user_proxy = autogen.UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=0,
        is_termination_msg=lambda m: "TERMINATE" in m.get("content", ""),
        code_execution_config=False,
        description="Poses the question and receives the final answer.",
    )

    planner = autogen.AssistantAgent(
        name="Planner",
        system_message=PLANNER_SYSTEM_MESSAGE,
        llm_config=llm_config,
        description="Turns the user's question into a search query. Speaks first, right after User.",
    )

    retriever = build_retriever(docs_path, config_list[0]["model"])

    responder = autogen.AssistantAgent(
        name="Responder",
        system_message=RESPONDER_SYSTEM_MESSAGE,
        llm_config=llm_config,
        description="Answers strictly from retrieved context and ends with TERMINATE. Speaks last.",
    )

    allowed_transitions = {
        user_proxy: [planner],
        planner: [retriever],
        retriever: [responder],
        responder: [user_proxy],
    }
    groupchat = autogen.GroupChat(
        agents=[user_proxy, planner, retriever, responder],
        messages=[],
        max_round=6,
        allowed_or_disallowed_speaker_transitions=allowed_transitions,
        speaker_transitions_type="allowed",
    )
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    return user_proxy, planner, retriever, responder, manager
