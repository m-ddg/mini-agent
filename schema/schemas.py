from pydantic import BaseModel
from typing import Any, Literal, Protocol, Optional
from ..tools import ToolResult
from enum import StrEnum


class Provider(StrEnum):
    """ LLM提供商 """

    OPENAI = 'openai'
    ANTHROPIC = 'anthropic'


class ToolCall(BaseModel):
    """ 工具调用封装格式 """

    id: str
    name: str
    type: str = 'function'   # 目前仅有调用函数 type = function
    arguments: dict[str, Any]


class Event(BaseModel):
    """ 用于适配事件驱动的responses api LLM调用 """

    type: Literal["user_text", "llm_text", "reasoning", "function_call", "function_output"]
    user_text: Optional[str] = None  # 记录用户的输入
    llm_text: Optional[str] = None  # 记录llm的文字输出
    thinking: Optional[str] = None  # 当事件类型为reasoning时，该属性记录LLM的推理内容
    tool_call: Optional[ToolCall] = None  # 当事件类型为function_call时，该属性记录LLM的工具调用
    tool_result: Optional[ToolResult] = None

class Message(BaseModel):
    """ 框架内消息结构 """

    role: Literal["system", "user", "assistant", "tool"]
    # 当role为system/user时，content是消息文本。
    # 用于responses api client时，当role为assistant或tool时，content是存储有事件的列表
    content: str | list[Event]


class TokenUsage(BaseModel):
    """ 记录token消耗，包括输入、输出和总计的消耗 """

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class LLMResponse(BaseModel):
    """ 封装来自LLM的原始返回 """

    message: Message  # 为避免字段重复，且方便从LLMResponse中拿到本轮的事件，故设置此属性
    finish_reason: str
    token_usage: TokenUsage


class RawResponseLike(Protocol):
    status: str
    output: list[Any]
    incomplete_details: Optional[Any]