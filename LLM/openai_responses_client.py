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
        base_url = base_url or os.getenv('OPENAI_API_URL', "https://openai.com/v1")
        model = model or "gpt-4o"
        super().__init__(api_key, base_url, model)
        self.client = AsyncClient(
            api_key=api_key,
            base_url=base_url,
        )
        self._cached_input_items = []
        self._idx = 0
        self._finish = False


    def _convert_events(self, events: list[Event]) -> tuple[dict[str, Any]]:
        """ 转换events为responses api格式的输入，并且每次都只对新增的events做转换 """

        new_events = events[self._idx:]

        for event in new_events:
            match event.type:
                case "user_text":
                    self._cached_input_items.append({
                        "role": "user",
                        "content": event.user_text
                    })

                case "llm_text":
                    self._cached_input_items.append({
                        "role": "assistant",
                        "content": event.llm_text
                    })

                case "function_call":
                    tc = event.tool_call
                    function_call_json = {
                        "arguments": json.dumps(tc.arguments),
                        "call_id": tc.id,
                        "name": tc.name,
                        "type": "function_call"
                    }
                    self._cached_input_items.append(function_call_json)

                case "function_output":
                    tr = event.tool_result
                    function_output_json = {
                        "call_id": tr.id,
                        "output": tr.content,
                        "type": "function_call_output"
                    }
                    self._cached_input_items.append(function_output_json)

        self._idx = len(events)
        # 返回元组防止意外修改私有属性
        return tuple(self._cached_input_items)

    def _clear_cache(self):
        self._cached_input_items = []
        self._idx = 0
        self._finish = False


    def _convert_tools(self, tools: Optional[BaseTool]) -> Optional[list[dict[str, Any]]]:
        """ 调用工具的to_schema方法获取responses api格式下的函数定义json """

        if not tools:
            return None

        tools_definitions = []
        for tool in tools:
            tools_definitions.append(tool.to_openai_responses_format())

        return tools_definitions


    def _parse_finish_reason(self, response: RawResponseLike) -> str:
        """ 从返回体解析出LLM调用结束的原因 """

        if any (item.type == "function_call" for item in response.output):
            return "Function call"
        match response.status:
            case "failed":
                return "请求整体失败。"
            case "cancelled":
                return "请求被取消"
            case "in_progress":
                return "流式处理中"
            case "queued":
                return "排队等待中"
            case "incomplete":
                reason_prefix = "返回被截断"
                reason = response.incomplete_details.reason
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
        output_events = []

        for item in output_items:
            match item.type:
                case "message":
                    total_text = ""
                    for part in item.content:
                        if part.type == "output_text":
                            total_text += part.text
                    text_event = Event(
                        type="llm_text",
                        llm_text=total_text,
                    )
                    output_events.append(text_event)

                case "reasoning":
                    thinking = ''
                    for part in item.summary:
                        thinking += part.text
                    reasoning_event = Event(
                        type="reasoning",
                        thinking=thinking
                    )
                    output_events.append(reasoning_event)

                case "function_call":
                    raw_args = item.arguments
                    try:
                        args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
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
                    output_events.append(tc_event)
                    if item.name == "Task Finish":
                        self.finish = True
                        break

        if self._finish:
            self._clear_cache()

        current_message = Message(
            role="assistant",
            content=output_events,
        )

        token_usage = TokenUsage(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            total_tokens=response.usage.total_tokens,
        )

        finish_reason = self._parse_finish_reason(response)

        result = LLMResponse(
            message=current_message,
            finish_reason=finish_reason,
            token_usage=token_usage
        )

        return result

    async def _make_api_request(
            self,
            system_prompt: str,
            input_items: list[dict[str, Any]],
            tools: Optional[list[Any]]
    ) -> RawResponseLike:
        """ 调用LLM """

        input_params = {
            "model": self.model,
            "instructions": system_prompt,
            "input": input_items,
            "tools": tools
        }
        response = await self.client.responses.create(**input_params)

        return response

    async def generate(
            self,
            system_prompt: str,
            events: list[Event],
            tools: Optional[list[BaseTool]] = None
    ) -> LLMResponse:
        """ client调用LLM的入口 """

        input_items = self._convert_events(events)
        input_items = list(input_items)
        tools_definitions = self._convert_tools(tools)

        response = await self._make_api_request(
            system_prompt = system_prompt,
            input_items = input_items,
            tools = tools_definitions
        )
        llm_response = self._parse_response(response)

        return llm_response









