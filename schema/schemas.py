from pydantic import BaseModel
from typing import Any
from enum import StrEnum


class Provider(StrEnum):
    """ LLM提供商 """
    OPENAI = 'openai'
    ANTHROPIC = 'anthropic'


class FunctionCall(BaseModel):
    """ 函数调用封装格式 """
    arguments: dict[str, Any]


class ToolCall(BaseModel):
    """ 工具调用封装格式 """
    id: str
    name: str
    type: str = 'function'   # 目前仅有调用函数 type = function
    function: FunctionCall


class Message(BaseModel):
    """ 框架内消息结构 """
    role: str # system, user, assistant, tool
    thinking: str | None = None
    content: str | list[dict[str, Any]]
    tool_calls: list[ToolCall] | None = None
    # 当role为tool时，下面两个属性的值不应为空，tool_calls需要为空
    tool_call_id: str | None  = None
    tool_call_name: str | None = None


class TokenUsage(BaseModel):
    """ 记录token消耗，包括输入、输出和总计的消耗 """
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class LLMResponse(BaseModel):
    """ 封装来自LLM的原始返回 """
    finish_reason: str
    thinking: str | None = None
    content: str
    tool_calls: list[ToolCall] | None = None
    token_usage: TokenUsage