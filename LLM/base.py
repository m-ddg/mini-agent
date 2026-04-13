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
    def _convert_message(
            self,
            messages: list[Message]
    ) -> tuple[str | None, dict[str, Any]]:
        """
        转换消息列表中的每一条消息为模型需要的输入格式，不对工具做格式转换

        Args:
            messages: 内置消息的列表

        Returns:
            返回一个二元组，第一个元素为系统提示词，第二个元素为适配处理后的请求消息
        """
        pass


    @abstractmethod
    def _prepare_request(
            self,
            messages: list[Message],
            tools: list[Any] | None = None
    ) -> dict[str, Any]:
        """
        生成LLM调用所需的输入，包含对工具的格式转换

        Args:
            messages: 内置消息的列表
            tools: 工具列表

        Returns:
            返回完整的LLM调用所需要的请求内容
        """
        pass

    @abstractmethod
    def generate(
            self,
            messages: list[Message],
            tools: list[Any] | None = None,
            model: str | None = None
    ) -> LLMResponse:
        """ 调用LLM """
        pass