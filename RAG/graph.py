from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver

from state import State
from graph_nodes import *
from tools import search_child_chunks, retrieve_parent_chunks

builder = StateGraph(State)

builder.add_node("summarize", analyze_chat_and_summarize)
builder.add_node("analyze_rewrite", analyze_and_rewrite_query)
builder.add_node("human_input", lambda s: {})
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode([search_child_chunks, retrieve_parent_chunks]))

builder.add_edge(START, "summarize")
builder.add_edge("summarize", "analyze_rewrite")
builder.add_conditional_edges("analyze_rewrite", route_after_rewrite)
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

agent_graph = builder.compile(
    checkpointer=InMemorySaver(),
    interrupt_before=["human_input"]
)
