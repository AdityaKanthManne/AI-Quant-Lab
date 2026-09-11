from typing import Any

from langgraph.graph import END, START, StateGraph

from fin_research.agents.filings import SecFilingAgent
from fin_research.agents.fundamentals import FundamentalsAgent
from fin_research.agents.macro import MacroAgent
from fin_research.agents.news import NewsSentimentAgent
from fin_research.agents.quantitative import QuantitativeSignalAgent
from fin_research.agents.supervisor import SupervisorAgent
from fin_research.data.providers import ResearchDataProvider
from fin_research.models.state import ResearchState


def build_research_graph(provider: ResearchDataProvider) -> Any:
    fundamentals = FundamentalsAgent(provider)
    filings = SecFilingAgent(provider)
    macro = MacroAgent(provider)
    news = NewsSentimentAgent(provider)
    quant = QuantitativeSignalAgent(provider)
    supervisor = SupervisorAgent()

    async def run_fundamentals(state: ResearchState) -> ResearchState:
        return {"fundamentals": await fundamentals.run(state["request"].ticker)}

    async def run_filings(state: ResearchState) -> ResearchState:
        return {"filings": await filings.run(state["request"].ticker)}

    async def run_macro(state: ResearchState) -> ResearchState:
        return {"macro": await macro.run(state["request"].ticker)}

    async def run_news(state: ResearchState) -> ResearchState:
        return {"news": await news.run(state["request"].ticker)}

    async def run_quant(state: ResearchState) -> ResearchState:
        return {"quant": await quant.run(state["request"].ticker)}

    def synthesize(state: ResearchState) -> ResearchState:
        return {"report": supervisor.run(state)}

    graph = StateGraph(ResearchState)
    workers = {
        "fundamentals": run_fundamentals,
        "filings": run_filings,
        "macro": run_macro,
        "news": run_news,
        "quant": run_quant,
    }
    for name, node in workers.items():
        graph.add_node(name, node)
        graph.add_edge(START, name)
        graph.add_edge(name, "supervisor")
    graph.add_node("supervisor", synthesize)
    graph.add_edge("supervisor", END)
    return graph.compile()
