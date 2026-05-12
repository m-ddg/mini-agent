import tiktoken


def _estimate_tokens_fallback(content: str) -> int:
    """ token 计算的兜底方式 """

    return int(len(content)/2.5)



def estimate_tokens(content: str) -> int:
    """ 计算传入字符串的 token 数量 """

    try:
        total_tokens = 0
        encoding = tiktoken.get_encoding("cl100k_base")
        total_tokens = len(encoding.encode(content))
        # 模拟元信息带来的额外token
        total_tokens += 100

        return total_tokens

    except Exception as e:
        print(e)
        return _estimate_tokens_fallback(content)