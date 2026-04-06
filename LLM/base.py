from pydantic import BaseModel, Field
from typing import Any

class BaseLLMClient(BaseModel):
    """ LLMClient的基类 """

    def