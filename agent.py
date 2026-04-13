from .schema import Message, Event
from typing import Any, Optional
import json

max_step = 50
messages = []
step = 0

def convert_message(
        self,
        messages: list[Message]
) -> tuple[str | None, list[dict[str, Any]]]:
    if not messages:
        raise ValueError('messages不能为空')

    system_prompt = ''
    input_events = []

    for msg in messages:
        match msg.role:
            case 'system':
                system_prompt = msg.content

            case 'user':
                temp_user_dict = {
                    "role": "user",
                    "content": msg.content
                }
                input_events.append(temp_user_dict)

            case 'assistant':
                for event in msg.content:
                    if event.type == "message":
                        text_dict = {
                            "role": "assistant",
                            "content": event.text
                        }
                        input_events.append(text_dict)
                    elif event.type == "function_call":
                        function_call_dict = {
                            "call_id": event.tool_call.id,
                            "type": "function_call",
                            "name": event.tool_call.name,
                            "arguments": json.dumps(event.tool_call.arguments)
                        }
                        input_events.append(function_call_dict)

            case "tool":
                for event in msg.content:
                    if event.type == "function_call_output":
                        function_call_output_dict = {
                            "type": "function_call_output",
                            "call_id": event.tool_result.id,
                            "output": event.tool_result.content
                        }
                        input_events.append(function_call_output_dict)

    return system_prompt, input_events
while step < max_step:
    mission_events = []
    system_prompt, input_events = convert_message(messages)
    mission_events += input_events




