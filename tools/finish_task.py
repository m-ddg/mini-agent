from .base import BaseTool

class FinishTask(BaseTool):

    parameters = None
    type = "function"

    @property
    def name(self):
        return "Finish Task"

    @property
    def description(self):
        return "当任务完成时，请调用这个函数以表明任务被完成"

    async def execute(self):
        return None
