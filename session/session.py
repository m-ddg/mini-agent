from ..schema import Task, Summary
from typing import Optional, Any
class Session:
    """ 会话层的抽象 """

    tasks: Optional[list[Task]] = None
    summaries: Optional[list[Summary]] = None