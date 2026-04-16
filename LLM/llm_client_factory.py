from . import BaseLLMClient, openai_responses_client
from .. schema import Provider

def create_llm_client(provider: str) -> BaseLLMClient:
    upper_provider = provider.upper()
    llm_providr = Provider.upper_provider

    match llm_providr:
        case "openai":
            return openai_responses_client()