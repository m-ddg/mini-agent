from . import BaseLLMClient, OpenAIResponsesClient, SummaryClient
from ..schema import Provider
from typing import Optional, Any

def create_llm_client(provider: str, model: Optional[str] = None) -> BaseLLMClient:
    """ 返回对应产商client的工厂函数 """

    upper_provider = provider.upper()
    llm_provider = Provider.upper_provider

    match llm_provider:
        case "openai":
            return OpenAIResponsesClient(model = model)



# **返回类型需要再确定一下**
def create_summary_client(provider: Optional[str] = None, model: Optional[str] = None) -> Any:
    """ 返回摘要 client 实例 """


    return SummaryClient(provider = provider, model = model)