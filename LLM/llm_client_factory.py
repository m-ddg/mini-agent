from . import BaseLLMClient, OpenAIResponsesClient
from .. schema import Provider

def create_llm_client(provider: str) -> BaseLLMClient:
    """ 返回对应产商client的工厂函数 """

    upper_provider = provider.upper()
    llm_provider = Provider.upper_provider

    match llm_provider:
        case "openai":
            return OpenAIResponsesClient()