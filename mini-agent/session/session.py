from ..schema import Task, Summary
from typing import Optional


class Session:
    """ 会话层的抽象 """

    _tasks: Optional[list[Task]] = None
    _summaries: Optional[list[Summary]] = None
    # 用于表示未被摘要的 task 的起始位置，_unsummary_task_count + 1 开始就是未被摘要的 task
    _unsummary_task_count: int = 0

    @property
    def tasks(self):
        return self._tasks

    @property
    def summaries(self):
        return self._summaries



