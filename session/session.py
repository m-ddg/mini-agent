from ..schema import Task, Summary
from typing import Optional, Any




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

    def get_user_input(self, user_input: Optional[str]):
        self._user_input = user_input


