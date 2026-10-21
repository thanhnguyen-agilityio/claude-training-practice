from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        description="User input to the agent.",
        examples=["Give me categories list."],
    )
    user_id: str = Field(
        description="User ID.",
        examples=["user_1"],
    )
    thread_id: str | None = Field(
        description="Thread ID to persist and continue a multi-turn conversation.",
        default=None,
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )

class ToolCallApprovalRequest(BaseModel):
    user_id: str = Field(
        description="User ID.",
        examples=["user_1"],
    )
    thread_id: str | None = Field(
        description="Thread ID to persist and continue a multi-turn conversation.",
        default=None,
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )
    tool_call_id: str = Field(
        description="Tool call ID to approve or reject.",
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )
    user_input: str = Field(
        description="User input to the agent.",
        examples=["The tool call is approved."],
    )


class ChatHistoryInput(BaseModel):
    """Input for retrieving chat history."""

    thread_id: str = Field(
        description="Thread ID to persist and continue a multi-turn conversation.",
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )
