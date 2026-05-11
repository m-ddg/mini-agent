from .schema import Task, Event
from .LLM import BaseLLMClient, create_llm_client, create_summary_client
from .tools import BaseTool
from .session import Session
from typing import Optional, Annotated
from pathlib import Path
from .utils import estimate_tokens


class Agent:
    """ agent的实现 """

    def __init__(
            self,
            provider: Optional[str] = None,
            llmclient: Optional[BaseLLMClient] = None,
            summary_client: Optional[BaseLLMClient] = None,
            max_step: int = 50,
            token_limit: int = 8000,
            system_prompt: Optional[str] = None,
            tools: Optional[list[BaseTool]] = None,
            task_type: str = "chat",
    ):

        if not (provider or llmclient):
            raise ValueError("请至少传入provider或llmclient二者中的一个参数以为agent配置LLMClient")

        self._client = llmclient or create_llm_client(provider)
        self._summary_client = summary_client or create_summary_client()
        self.max_step = max_step
        self._system_prompt = self._get_system_prompt(system_prompt)
        self.tools = tools
        self.tool_dict = {tool.name: tool for tool in tools} if tools else {}
        self.task_type = task_type
        self._should_summary: bool = False

        self._hot_soft_ratio = 0.6
        self._hot_hard_ratio = 0.8


    @property
    def system_prompt(self):
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, value):
        self._system_prompt = value



    def _create_system_prompt(self, system_prompt: Optional[str] = None) -> str:
        """ 创建系统提示词 """

        if system_prompt:
            return system_prompt

        system_prompt_path = Path("mini_agent/config/system_prompt.md")
        if system_prompt_path.exists():
            system_prompt = system_prompt_path.read_text(encoding="utf-8")
            return system_prompt

        return "You are a helpful AI assistant that can use tools."


    def create_user_input_event(self, content: str) -> Event:
        """ 为 messages 添加用户的输入 """

        user_input_event = Event(
            type = 'user_text',
            user_text = content
        )

        return user_input_event


#     def summary_messages(self) -> None:
#         """ 压缩/摘要函数 """
#
#         if self._should_summary:
#             summary_boundry = self.task_count - self.no_summary_limit
#
#             saved_messages = []
#             try:
#                 text_need_summary = ''
#                 for msg in self.messages:
#                     if msg.task_count <= summary_boundry:
#                         match msg.role:
#                             case 'user':
#                                 text_need_summary += f"用户：{msg.content}\n"
#
#                             case 'assistant':
#                                 for event in msg.content:
#                                     if event.type == 'llm_text':
#                                         text_need_summary += f"llm:{event.llm_text}\n"
#                                     elif event.type == 'function_call':
#                                         text_need_summary += f"llm:调用工具{event.tool_call.name}\n"
#
#                             case 'tool':
#                                 for event in msg.content:
#                                     text_need_summary += (f"工具{event.tool_result.name}执行结果："
#                                                           f"{event.tool_result.content}\n")
#
#                     else: saved_messages.append(msg)
#
#                 summary_prompt = f"""
# 请你对以下的用户与大模型的交互过程进行总结，并在总结时遵循以下规则：
# 1. **请不要过度缩略用户的输入**
# 2. 请主要对llm的输出做总结，总结结果请保留要点
# 下面是待被总结的交互过程
# {text_need_summary}
# """
#
#                 summary_client = create_llm_client('')
#                 summary_result = summary_client.generate(summary_prompt)
#
#             except Exception as e:
#                 print(e)



    def convert_tasks_to_events(
            self,
            tasks: list[Task]
    ) ->  list[Event]:
        """ 转换 tasks 为 events """

        if not tasks:
            raise ValueError('tasks不能为空')

        current_events = []

        for task in tasks:
            for event in task.events:
                if event.type != 'reasoning':
                    current_events.append(event)

        return current_events



    def build_context(self, session: Session, user_input: str) -> list[Event]:
        """ 创建上下文 """

        # **这里需要先把系统提示词，工具定义，本轮输入转化为字符串用于token计算
        # system_prompt_tokens = estimate_tokens(self.system_prompt)
        # tools_tokens = estimate_tokens(self.tools)
        # input_tokens = estimate_tokens(self.task_type)
        # remaning_tokens = self._client.context_window


    # ↓还需改进
    async def run(self, session: Session) -> None:
        """ 运行单次任务（用户输入） """

        step = 0
        current_events = []

        history_tasks = session.tasks

        input_events = self.convert_tasks_to_events(history_tasks)

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






