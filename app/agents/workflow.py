from __future__ import annotations

from typing import Any
from app.agents.fact_check_agent import fact_check_agent
from langgraph.graph import END, START, StateGraph

from app.agents.research_agent import research_agent
from app.agents.state import WorkflowState
from app.agents.script_agent import script_agent    


def initialize_workflow(state: WorkflowState) -> WorkflowState:
    """Initialize the content-generation workflow state."""

    return {
        **state,
        "research_notes": state.get("research_notes", []),
        "claims": state.get("claims", []),
        "qa_errors": state.get("qa_errors", []),
        "qa_pass": state.get("qa_pass", False),
    }


def build_workflow() -> Any:
    """Build and compile the content-generation workflow."""

    graph = StateGraph(WorkflowState)

    graph.add_node("initialize", initialize_workflow)
    graph.add_node("research", research_agent)
    graph.add_node("script", script_agent)
    graph.add_node("fact_check", fact_check_agent)

    graph.add_edge(START, "initialize")
    graph.add_edge("initialize", "research")
    graph.add_edge("research", "script")
    graph.add_edge("script", "fact_check")
    graph.add_edge("fact_check", END)

    return graph.compile()