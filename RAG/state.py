from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing import List

class State(MessagesState):
    questionIsClear: bool
    conversation_summary: str = ""

class QueryAnalysis(BaseModel):
    is_clear: bool = Field(
        description="Indicates if the user's question is clear and answerable."
    )
    questions: List[str] = Field(
        description="List of rewritten, self-contained questions."
    )
    clarification_needed: str = Field(
        description="Explanation if the question is unclear."
    )