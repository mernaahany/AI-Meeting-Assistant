from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, RemoveMessage
from typing import Literal 
from typing import List 
from tools import llm_with_tools
from llm_setup import llm
from state import State
from state import QueryAnalysis
from prompts import agent_system_message




def analyze_chat_and_summarize(state: State):
    """
    Analyzes chat history and summarizes key points for context.
    """
    # Need history (Q1 + A1) to summarize for the *second* turn onwards
    if len(state["messages"]) < 2:
        return {"conversation_summary": ""}

    # Extract relevant messages (excluding current query and system messages)
    # state["messages"][-1] is the current user query
    relevant_msgs = [
        msg for msg in state["messages"][:-1]
        if isinstance(msg, (HumanMessage, AIMessage))
        and not getattr(msg, "tool_calls", None)
    ]

    if not relevant_msgs:
        return {"conversation_summary": ""}

    summary_prompt = """**Summarize the key topics and context from this conversation concisely (1-2 sentences max).**
    Discard irrelevant information, such as misunderstandings or off-topic queries/responses.
    If there are no key topics, return an empty string.

    """
    for msg in relevant_msgs[-6:]:  # Last 6 messages for context
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        summary_prompt += f"{role}: {msg.content}\n"

    summary_prompt += "\nBrief Summary:"

    # FIX: The Gemini API requires a non-system message.
    messages_for_llm = [
        SystemMessage(content=summary_prompt),
        HumanMessage(content="Proceed with the summary based on the history provided in the system message.")
    ]
    
    # Assuming 'llm' is defined outside this function and is available
    summary_response = llm.with_config(temperature=0.3).invoke(messages_for_llm)
    return {"conversation_summary": str(summary_response.content)}

def analyze_and_rewrite_query(state: State):
    """
    Analyzes user query and rewrites it for clarity, optionally using conversation context.
    """
    last_message = state["messages"][-1]
    raw_summary = state.get("conversation_summary", "")

    if isinstance(raw_summary, list):
        conversation_summary = str(raw_summary[-1]) if raw_summary else ""
    else:
        conversation_summary = str(raw_summary)

    context_section = (
        f"**Conversation Context:**\n{conversation_summary}"
        if conversation_summary.strip()
        else "**Conversation Context:**\n[First query in conversation]"
    )

    # Create analysis prompt
    prompt = f"""
    **Rewrite the user's query** to be clear, self-contained, and optimized for information retrieval.

    **User Query:**
    "{last_message.content}"

    {context_section}

    **Instructions:**

    1. **Resolve references for follow-ups:**
    - If the query uses pronouns or refers to previous topics, use the context to make it self-contained.

    2. **Ensure clarity for new queries:**
    - Make the query specific, concise, and unambiguous.

    3. **Correct errors and interpret intent:**
    - If the query is grammatically incorrect, contains typos, or has abbreviations, correct it and infer the intended meaning.

    4. **Split only when necessary:**
    - If multiple distinct questions exist, split into **up to 3 focused sub-queries** to avoid over-segmentation.
    - Each sub-query must still be meaningful on its own.

    5. **Optimize for search:**
    - Use **keywords, proper nouns, numbers, dates, and technical terms**.
    - Remove conversational filler, vague words, and redundancies.
    - Make the query concise and focused for information retrieval.

    6. **Mark as unclear if intent is missing:**
    - This includes nonsense, gibberish, insults, or statements without an apparent question.
    """

    # Assuming 'llm' is available
    llm_with_structure = llm.with_config(temperature=0.3).with_structured_output(QueryAnalysis)
    response = llm_with_structure.invoke([HumanMessage(content=prompt)])

    if response.is_clear:
        # Get the ID of the last message (the original query) to be replaced
        last_human_message_id = state["messages"][-1].id

        # Format rewritten query
        rewritten = (
            "\n".join([f"{i+1}. {q}" for i, q in enumerate(response.questions)])
            if len(response.questions) > 1
            else response.questions[0]
        )
        
        # FIX: Use RemoveMessage for the old query's ID and add the new HumanMessage.
        # This replaces the message in the history cleanly.
        return {
            "questionIsClear": True,
            "messages": [
                RemoveMessage(id=last_human_message_id),
                HumanMessage(content=rewritten)
            ]
        }
    else:
        clarification = response.clarification_needed or "I need more information to understand your question."
        return {
            "questionIsClear": False,
            "messages": [AIMessage(content=clarification)]
        }

def human_input_node(state: State):
    """Placeholder node for human-in-the-loop interruption"""
    return {}

def route_after_rewrite(state: State) -> Literal["agent", "human_input"]:
    """Route to agent if question is clear, otherwise wait for human input"""
    return "agent" if state.get("questionIsClear", False) else "human_input"

def agent_node(state: State):
    """Main agent node that processes queries using tools"""
    
    # MessagesState handles message removal/merging automatically before this node is run.
    # The message history is now guaranteed to be clean (no RemoveMessages).
    messages = [agent_system_message] + state["messages"]

    # Ensure there is at least one HumanMessage
    if not any(isinstance(m, HumanMessage) for m in messages):
        # This block might catch first-run scenarios if state["messages"] is empty/modified oddly
        messages.append(HumanMessage(content="User query here"))

    # Assuming 'llm_with_tools' is available
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}