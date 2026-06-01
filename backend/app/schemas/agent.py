from pydantic import BaseModel, Field


class AgentChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=2000)


class AgentChatReq(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    history: list[AgentChatMessage] = Field(default_factory=list, max_length=10)


class AgentToolResult(BaseModel):
    tool: str
    summary: str
    data: dict | list | None = None


class AgentChatResp(BaseModel):
    reply: str
    intent: str
    tool_results: list[AgentToolResult] = Field(default_factory=list)
    need_login: bool = False
