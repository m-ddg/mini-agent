from pydantic import BaseModel, Field
from typing import Any


class FunctionCall(BaseModel):
    function_name: str
    args: B


class ToolCall(BaseModel):
    tool_call: str
    type: str = 'function'   # 目前仅有调用函数 type = function
    function: FunctionCall

class Message(BaseModel):
    """ 框架内消息结构 """

    role: str # system, user, assistant, tool
    thinking: str | None
    content: str | list[dict[str, Any]]
    tool_calls: list[ToolCall] = None
    # 当role为tool时，下面两个属性的值不应为空，tool_calls需要为空
    tool_call_id: str = None
    tool_call_name: str = None
