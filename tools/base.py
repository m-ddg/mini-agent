import inspect
from pydantic import BaseModel, create_model
from typing import Any, Callable, Literal


class ToolResult(BaseModel):
    """ 记录工具的执行结果 """

    id: str
    name: str
    success: bool
    content: str = ''
    error: str | None = None


class BaseTool(BaseModel):
    """ 工具基类，创建工具时应继承该基类 """

    # 工具的参数
    parameters: BaseModel

    #工具的类型
    type: Literal['function', 'coding'] = 'function'

    # 工具的名字
    @property
    def name(self) -> str:
        raise NotImplementedError

    # 工具的描述
    @property
    def description(self) -> str:
        raise NotImplementedError

    async def execute(self, *args, **kwargs) -> ToolResult:
        """ 执行工具 """
        raise NotImplementedError

    @staticmethod
    def clean_schema(json_data: dict[str, Any]) -> dict[str, Any]:
        """ 转换parameters.model_json_schema()返回的字典为干净的格式 """
        json_data.pop('title')
        for k, v in json_data['properties'].items():
            v.pop('title')
        json_data['additionalProperties'] = False
        return json_data


    def to_openai_response_format(self) -> dict[str, Any]:
        """ 将工具转为OpenAI的response api的定义格式 """
        param_dict = self.clean_schema(self.parameters.model_json_schema())
        return {
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'parameters': param_dict
        }

    def to_openai_chat_format(self) -> dict[str, Any]:
        """ 将工具转换为OpenAI的chat completions的定义格式 """
        param_dict = self.clean_schema(self.parameters.model_json_schema())
        return {
            "type": self.type,
            self.type: {
                "name": self.name,
                "description": self.description,
                "strict": True,
                "parameters": param_dict
            }
        }


class FunctionTool(BaseTool):
    """ 函数工具的基类，主要用于创建简单的函数工具，支持通过传入函数创建工具 """

    func_name: str
    func_description: str
    parameters: type[BaseModel]
    func: Callable

    @property
    def name(self) -> str:
        return self.func_name

    @property
    def description(self) -> str:
        return self.func_description

    async def execute(self, parameters, *args, **kwargs) -> ToolResult:
        try:
            if inspect.iscoroutinefunction(self.func):
                res = await self.func(parameters, *args, **kwargs)
            else:
                res = self.func(parameters, *args, **kwargs)
            return ToolResult(success = True, content = str(res))
        except Exception as e:
            return ToolResult(success = False, error = str(e))

    @classmethod
    def create_tool(cls, func: Callable[[Any], Any]) -> "FunctionTool":
        name = func.__name__
        description = func.__doc__
        fields = {}
        sig = inspect.signature(func)
        for param_name, param in sig.parameters.items():
            param_type = param.annotation if param.annotation != inspect._empty else Any
            param_default = param.default if param.default != inspect._empty else None
            fields[param_name] = (param_type, param_default)
        ParamSchema = create_model(name = f"{name}Schema", **fields)

        return cls(
            func_name = name,
            func_description = description,
            func = func,
            parameters = ParamSchema(),
        )




