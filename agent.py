from .schema import Message, Event
from .LLM import BaseLLMClient,create_llm_client
from .tools import BaseTool
from typing import Any, Optional
from pathlib import Path


class Agent:
    """ agent的实现 """

    def __init__(
            self,
            provider: Optional[str] = None,
            llmclient: Optional[BaseLLMClient] = None,
            max_step: int = 50,
            token_limit: int = 8000,
            system_prompt: Optional[str] = None,
            tools: Optional[list[BaseTool]] = None,
            task_type: str = "chat",
    ):

        if not (provider or llmclient):
            raise ValueError("请至少传入provider或llmclient二者中的一个参数以为agent配置LLMClient")

        self._client = llmclient or create_llm_client(provider)
        self.max_step = max_step
        self.token_limit = token_limit
        self._system_prompt = self._get_system_prompt(system_prompt)
        self.messages = []
        self.tools = tools
        self.tool_dict = {tool.name: tool for tool in tools} if tools else {}
        self.task_type = task_type
        self._should_summary: bool = False
        self.task_count = 0


    @property
    def system_prompt(self):
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, value):
        self._system_prompt = value



    def _get_system_prompt(self, system_prompt: Optional[str] = None) -> str:
        """ 创建系统提示词 """

        if system_prompt:
            return system_prompt

        system_prompt_path = Path("mini_agent/config/system_prompt.md")
        if system_prompt_path.exists():
            system_prompt = system_prompt_path.read_text(encoding="utf-8")
            return system_prompt

        return "You are a helpful AI assistant that can use tools."


    def build_user_message(self) -> None:
        """ 为 messages 添加用户的输入 """

        user_input = input("聊些什么呢？")
        user_input = user_input.strip()
        user_message = Message(role='user', content=user_input)
        self.messages.append(user_message)


    def summary_messages(self) -> None:
        """ 压缩/摘要函数 """

        if self._should_summary:
            try:
                text_need_summary = ''
                for msg in self.messages:
                    pass



    def convert_message(
            self,
            messages: list[Message]
    ) ->  list[Event]:
        """ 转换 messages 为 events """

        if not messages:
            raise ValueError('messages不能为空')

        input_events = []

        for msg in messages:
            match msg.role:
                case 'user':
                    user_event = Event(
                        type="user_text",
                        user_text=msg.content
                    )
                    input_events.append(user_event)

                case 'assistant':
                    for event in msg.content:
                        if event.type != "reasoning":
                            input_events.append(event)

                case "tool":
                    for event in msg.content:
                        input_events.append(event)

        return input_events


    async def run(self, messages: list[Message], system_prompt: Optional[str] = None) -> None:
        """ 运行单次任务（用户输入） """

        self.task_count += 1
        step = 0
        task_events = []
        input_events = self.convert_message(messages)
        task_events += input_events
        finish = False

        while step < self.max_step:

            response = await self._client.generate(
                system_prompt = system_prompt or self._system_prompt,
                input_events = task_events,
                tools = self.tools
            )

            output_message = response.message
            output_message.task_count = self.task_count
            messages.append(output_message)

            output_events = output_message.content
            tool_call_list = []

            for event in output_events:
                match event.type:
                    case "llm_text":
                        task_events.append(event)

                    case "reasoning":
                        continue

                    case "function_call":
                        if event.tool_call.name == "Finish Task":
                            finish = True
                            break
                        else:
                            task_events.append(event)
                            tool_call_list.append(event.tool_call)

            if finish:
                current_token = response.token_usage.input_tokens
                if current_token > self.token_limit:
                    self._should_summary = True
                break

            tool_result_events = []
            for tc in tool_call_list:
                tool = self.tool_dict.get(tc.name)
                tr = await tool.execute(tc)
                tool_result_event = Event(
                    type = "function_output",
                    tool_result = tr
                )
                tool_result_events.append(tool_result_event)

            task_events.extend(tool_result_events)
            tool_message = Message(
                role = "tool",
                content = tool_result_events,
                task_count = self.task_count
            )
            messages.append(tool_message)

            step += 1






