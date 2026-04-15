from typing import Any
from ..schema import Message, LLMResponse
from ..tools import BaseTool
from abc import ABC, abstractmethod

class BaseLLMClient(ABC):
    """ LLM Client的基类 """

    def __init__(
            self,
            api_key: str | None = None,
            base_url: str | None = None,
            model: str | None = None,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model


    @abstractmethod
    def generate(
            self,
            messages: list[Message],
            tools: list[Any] | None = None,
            model: str | None = None
    ) -> LLMResponse:
        """ 调用LLM """
        pass