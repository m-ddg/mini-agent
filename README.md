# mini-agent-
一个简易的agent框架，很大程度上参考了MiniMax的Mini-Agent框架https://github.com/MiniMax-AI/Mini-Agent

2026/04/13-04/14
- 新增了RawResponseLike类用于抽象responses api格式下返回体的协议
- 新增了从返回体中解析出finish reason的函数_parse_finsih_reason
- 修改了_parse_response函数的逻辑，值的获取从字典索引[]改为属性访问.。（原来openai官网的文档演示的返回体的字典格式和sdk时不一样的，sdk下返回体是一个List[ResponseOutputItem]，且其中的嵌套属性也依然是类的实例）
- 写了一点agent的循环框架
