from ..schema import Task, Summary
from typing import Optional


class Session:
    """ 会话层的抽象 """

    _tasks: Optional[list[Task]] = None
    _summaries: Optional[list[Summary]] = None
    _user_input: Optional[str] = None

    @property
    def tasks(self):
        return self._tasks

    @property
    def summaries(self):
        return self._summaries



