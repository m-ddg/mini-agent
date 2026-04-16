# mini-agent-
一个简易的agent框架，很大程度上参考了MiniMax的Mini-Agent框架https://github.com/MiniMax-AI/Mini-Agent

2026/04/13
- 新增了RawResponseLike类用于抽象responses api格式下返回体的协议
- 新增了从返回体中解析出finish reason的函数_parse_finsih_reason
- 修改了_parse_response函数的逻辑，值的获取从字典索引[]改为属性访问.。（原来openai官网的文档演示的返回体的字典格式和sdk时不一样的，sdk下返回体是一个List[ResponseOutputItem]，且其中的嵌套属性也依然是类的实例）
- 写了一点agent的循环框架


2026/04/14
- 修改了结构的设计。原本的设计下，agent层会维护一个记录session内产生的所有的message的messages: list[Message]；以及一个仅限于单次task，记录单次task所产生的所有的事件的events: list[input_dict]，不过这个events里的元素直接就是符合api输入格式的，events可以直接用于client.response.create(input = events)。task内的后续调用直接做增量更新，而非每次调用都重复从messages解析。
不过这种在agent层就解析出api格式的输入会污染agent层，导致agent层无法被复用于其他厂商。
- 做出的一个修改是，将原本的messages -> events: list[input_dict]流程拆成了两部分。
第一部分是 messages -> events: lsit[Event]，并且保留在agent层，以适配记录LLM输出和工具执行结果两种事件的需求。
第二部分是 events -> input_items: list[input_dict]，这一部分移回LLMClient层，来做从事件到responses api格式输入的转换。
- 第二个修改是，由于现在从messages到input_items中间隔了一个evens，因此需要新增一种用户输入的事件，才能将用户输入转为input_dict。因此也修改了Event，新增了type的一个可取值，user_text，以及一个属性user_text。
- 第三个修改是，原本的Event的type可取值是和openai的responses api格式对齐的，为了后续做多厂商适配，修改了部分type的可取值。


2026/04/15
- 注意到输入的构造用dict/json，但是sdk返回的输出是类实例，通过属性访问获取内容，为此修改了部分的函数

- 在chat的建议下将event -> input_items的转换放回LLMClient层，并初步实现了增量转换函数。

- 虽然实现了增量更新的events -> input_items的转换，但是纠结是否应该返回结果，因为函数的实现是靠更新私有的实例属性来实现的，在调用LLM时，可以访问私有属性获取input，也可以通过调用函数获取input。最终选择让函数返回结果，转换函数作为私有属性对外的唯一访问接口。

- 纠结是否应该有prepare函数？event转换函数和工具转换函数是否要塞进prepare做一层额外封装？以及两个convert函数/prepare函数是放在make函数之前形成串行结构，还是放在make函数内？
最终决定不写prepare函数，两个convert函数放在make函数前。

- 为了适配现在的reponses api client，决定砍掉BaseLLMClient基类除generate函数外的所有约束，格式的转换留给子类实现。不得不说，这个提议既大胆又合理。