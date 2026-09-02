from langgraph.graph import StateGraph, START, END

from src.agent.state import ValidationState
from src.agent.nodes import (
    validate_pair_node,
    run_core_validations_node,
    final_decision_node,
    pair_route,
)


def build_validation_graph():
    graph = StateGraph(ValidationState)

    graph.add_node("validate_pair", validate_pair_node)
    graph.add_node("run_core_validations", run_core_validations_node)
    graph.add_node("final_decision", final_decision_node)

    graph.add_edge(START, "validate_pair")
    graph.add_conditional_edges(
        "validate_pair",
        pair_route,
        {
            "continue": "run_core_validations",
            "stop": "final_decision",
        },
    )
    graph.add_edge("run_core_validations", "final_decision")
    graph.add_edge("final_decision", END)

    return graph.compile()