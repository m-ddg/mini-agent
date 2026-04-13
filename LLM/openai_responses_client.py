import json
from .base import BaseLLMClient
from ..schema import Message, LLMResponse, Event, ToolCall,TokenUsage, RawResponseLike
from ..tools import BaseTool
from typing import Any, Literal, Optional
import os
from dotenv import load_dotenv
from openai import AsyncClient

load_dotenv()


class OpenAIResponsesClient(BaseLLMClient):
    """ 处理responses api格式的OpenAI适配客户端 """


    def __init__(
            self,
            api_key: str | None = None,
            base_url: str | None = None,
            model: Literal['gpt-4o', 'gpt-4o-mini'] | None = "gpt-4o"
    ):
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        base_url = base_url or os.getenv('OPENAI_API_URL', "https://openai.com/api/v3/")
        model = model or "gpt-4o"
        super().__init__(api_key, base_url, model)
        self.client = AsyncClient(
            api_key=api_key,
            base_url=base_url,
        )


    def _parse_finsih_reason(self, response: RawResponseLike) -> str:
        """ 从返回体解析出LLM调用结束的原因 """

        if any (item.type == "funciton_call" for item in response.output):
            return "Funciton call"
        match response.status:
            case "failed":
                return "请求整体失败。"
            case "cancelled":
                return "请求被取消"
            case "in_porgress":
                return "流式处理中"
            case "queued":
                return "排队等待中"
            case "incomplete":
                reason_prefix = "返回被截断"
                reason = response.incomplete_deatils.reason
                if reason == "max_output_tokens":
                    return reason_prefix + "，超出最大输出token限制"
                elif reason == "content_filter":
                    return reason_prefix + "，触发了内容过滤机制"
                else: raise ValueError("返回了不可能的截断原因")
            case "completed":
                return "响应正常完成"


    def _parse_response(
                self,
                response: RawResponseLike
        ) -> LLMResponse:
        """ 解析LLM输出，将输出封装为Message """

        output_items = response.output
        # 存储本次调用所产生的所有事件
        current_events = []

        for item in output_items:
            match item.type:
                case "message":
                    total_text = ""
                    for part in item.content:
                        if part.type == "output_text":
                            total_text += part.text
                    text_event = Event(
                        type="message",
                        text=total_text,
                    )
                    current_events.append(text_event)

                case "reasoning":
                    thinking = ''
                    for part in item.summary:
                        thinking += part.text
                    reasoning_event = Event(
                        type="reasoning",
                        thinking=thinking
                    )
                    current_events.append(reasoning_event)

                case "function_call":
                    raw_args = item.arguments
                    try:
                        args = json.load(raw_args) if isinstance(raw_args, str) else raw_args
                    except json.JSONDecodeError:
                        args = {}
                    tc = ToolCall(
                        id=item.id,
                        name=item.name,
                        type="function",
                        arguments=args,
                    )
                    tc_event = Event(
                        type="function_call",
                        tool_call=tc
                    )
                    current_events.append(tc_event)

        current_message = Message(
            role="assistant",
            content=current_events,
        )

        token_usage = TokenUsage(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            total_tokens=response.usage.total_tokens,
        )

        finish_reason = self._parse_finsih_reason(response)

        result = LLMResponse(
            message=current_message,
            finish_reason=finish_reason,
            token_usage=token_usage
        )

        return result

    def _make_api_call(
            self,
            input_items: list[dict[str, Any]],
            tools: Optional[list[Any]]
    ) -> RawResponseLike:






