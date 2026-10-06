
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage

from src.llm.client import get_langchain_llm
from src.llm.prompts import SYSTEM_PROMPT
from src.tools.plot_tools import reset_generated_charts, get_generated_charts

from src.tools.langchain_tools import LANGCHAIN_TOOLS

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


llm = get_langchain_llm()
llm_with_tools = llm.bind_tools(LANGCHAIN_TOOLS)

def agent_node(state: AgentState) -> dict:
    """Le LLM décide : appeler un tool ou répondre."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


tool_node = ToolNode(LANGCHAIN_TOOLS)


def should_continue(state: AgentState) -> str:
    """Si le dernier message a des tool_calls → tools, sinon → END."""
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


graph_builder = StateGraph(AgentState)

graph_builder.add_node("agent", agent_node)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges(
    "agent",
    should_continue,
    {"tools": "tools", END: END},
)
graph_builder.add_edge("tools", "agent")  

graph = graph_builder.compile()


def run_agent_langgraph(user_question, history=None, verbose=True):
    """
    Même signature que run_agent, mais utilise le graphe LangGraph.
    """
    reset_generated_charts()
    if history is None:
        history = []

    from langchain_core.messages import HumanMessage, AIMessage
    lc_history = []
    for m in history:
        if m["role"] == "user":
            lc_history.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            lc_history.append(AIMessage(content=m["content"]))

    inputs = {"messages": lc_history + [HumanMessage(content=user_question)]}

    try:
        final_state = None
        for event in graph.stream(
            inputs,
            stream_mode="values",
            config={"recursion_limit": 15},   
        ):
            final_state = event
            if verbose:
                last = event["messages"][-1]
                if getattr(last, "tool_calls", None):
                    for tc in last.tool_calls:
                        print(f"🔧 Tool: {tc['name']}({tc['args']})")
    except Exception as e:
        return {
            "answer": f"⚠️ L'agent n'a pas conclu : {e}",
            "messages": final_state["messages"] if final_state else [],
            "history": history + [
                {"role": "user", "content": user_question},
                {"role": "assistant", "content": "(pas de réponse)"},
            ],
            "turns": 20,
            "artifacts": get_generated_charts(),
        }

    last_message = final_state["messages"][-1]

    new_history = history + [
        {"role": "user", "content": user_question},
        {"role": "assistant", "content": last_message.content},
    ]

    return {
        "answer": last_message.content,
        "messages": final_state["messages"],
        "history": new_history,
        "turns": sum(1 for m in final_state["messages"] if m.type == "ai"),
        "artifacts": get_generated_charts(),
    }

