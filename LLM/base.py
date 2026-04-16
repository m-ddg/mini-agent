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
    def generate(self, *args, **kwargs) -> LLMResponse:
        """ 调用LLM """
        pass