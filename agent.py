from .schema import Message, Event
from .LLM import create_llm_client
from typing import Any, Optional


class Agent:
    """ agent的实现 """

    def __init__(self, task_type, provider):
        self.task_type = task_type
        self.provider = provider
        self._client = create_llm_client(self.provider)
        self.messages = []
        self.max_step = 50
        self.tools = []
        self.tool_dict = {}

    def build_user_message(self):
        user_input = input("聊些什么呢？")
        user_message = Message(role='user', content=user_input)

        self.messages.append(user_message)


    def convert_message(
            self,
            messages: list[Message]
    ) -> tuple[Optional[str], list[Event]]:

        if not messages:
            raise ValueError('messages不能为空')

        system_prompt = ''
        input_events = []

        for msg in messages:
            match msg.role:
                case 'system':
                    system_prompt = msg.content

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

        return system_prompt, input_events

    def run(self, messages: list[Message]):
        """ 运行单次任务（用户输入） """

        step = 0
        task_events = []
        system_prompt, input_events = self.convert_message(messages)
        task_events += input_events
        finish = False

        while step < self.max_step:

            response = self._client.generate(
                system_prompt = system_prompt,
                input_events = task_events,
                tools = self.tools
            )

            output_message = response.message
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
                break

            tool_result_events = []

            for tc in tool_call_list:
                tool = self.tool_dict.get(tc.name)
                tr = tool.execute(tc)
                tool_result_event = Event(
                    type = "function_output",
                    tool_result = tr
                )
                tool_result_events.append(tool_result_event)

            task_events.extend(tool_result_events)
            tool_message = Message(
                role = "tool",
                content = tool_result_events
            )
            messages.append(tool_message)

            step += 1




