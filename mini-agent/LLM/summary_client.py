from pydantic import BaseModel
from . import create_llm_client
from typing import Optional


class SummaryClient(BaseModel):
    """ 摘要client的基类 """


    provider: Optional[str] = None
    model: Optional[str] = None

    # 暂时使用 response_api_client作为summary client
    summary_client = create_llm_client(provider = provider or "openai", model = model)

    context_window = summary_client.context_window
    summary_ratio = 0.9
    summary_limit = context_window * summary_ratio


    def should_summary(self, unsummary: str) -> bool:
        """ 判断该函数的输入（通常是session的tasks中未被摘要的的部分的内容）是否需要被摘要 """


    def create_summary(self, unsummary: str) -> str:
        """ 返回摘要结果 """
