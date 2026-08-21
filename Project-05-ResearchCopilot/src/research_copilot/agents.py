from __future__ import annotations

from itertools import pairwise
from typing import Any, Protocol, TypedDict

from langgraph.graph import END, START, StateGraph


class ResearchState(TypedDict, total=False):
    project_id: str
    research_question: str
    papers: list[dict[str, Any]]
    extractions: list[dict[str, Any]]
    gaps: list[str]
    hypotheses: list[str]
    datasets: list[dict[str, Any]]
    experiment_spec: dict[str, Any]
    generated_code: str
    code_approved: bool
    results: dict[str, Any]
    critique: list[str]
    report: str
    audit_log: list[str]


class Agent(Protocol):
    name: str

    async def __call__(self, state: ResearchState) -> dict[str, Any]: ...


class RoleAgent:
    """A dependency-injected role: deterministic services or an LLM can implement its handler."""

    def __init__(self, name: str, handler: Any | None = None):
        self.name = name
        self.handler = handler

    async def __call__(self, state: ResearchState) -> dict[str, Any]:
        if self.handler:
            update = await self.handler(state)
        else:
            update = {}
        return {**update, "audit_log": [*state.get("audit_log", []), self.name]}


AGENT_NAMES = (
    "literature_search",
    "paper_extraction",
    "research_gap",
    "hypothesis",
    "dataset_discovery",
    "experimental_design",
    "statistical_analysis",
    "code_execution",
    "critic_reviewer",
    "report_generation",
)


def build_research_graph(handlers: dict[str, Any] | None = None):
    """Compile the lifecycle graph; execution is gated by the approval router."""
    handlers = handlers or {}
    graph = StateGraph(ResearchState)
    for name in AGENT_NAMES:
        graph.add_node(name, RoleAgent(name, handlers.get(name)))

    ordered = AGENT_NAMES[:7]
    graph.add_edge(START, ordered[0])
    for current, following in pairwise(ordered):
        graph.add_edge(current, following)
    graph.add_conditional_edges(
        "statistical_analysis",
        lambda state: "execute" if state.get("code_approved") else "review",
        {"execute": "code_execution", "review": "critic_reviewer"},
    )
    graph.add_edge("code_execution", "critic_reviewer")
    graph.add_edge("critic_reviewer", "report_generation")
    graph.add_edge("report_generation", END)
    return graph.compile()
