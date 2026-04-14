from .schema import Message, Event
from typing import Any, Optional
import json

max_step = 50
messages = []
tools = []
step = 0

user_input = input("聊些什么呢？")
user_message = Message(role='user', content=user_input)
messages.append(user_message)

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

while step < max_step:

    task_events = []
    system_prompt, input_events = convert_message(messages)
    task_events += input_events

    response = client.generate(
        system_prompt = system_prompt,
        input_events = input_events,
        tools = tools
    )

    output_message = response.message
    output_events = output_message.content

    messages.append(output_message)

    for event in output_events:
        if event.type != "reasoning":
            task_events.append(event)

    step += 1




