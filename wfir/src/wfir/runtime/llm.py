from typing import Any, Optional, List
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

class MockChatModel(BaseChatModel):
    model_name: str = "mock"
    
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, run_manager: Optional[Any] = None, **kwargs: Any) -> ChatResult:
        last_msg = messages[-1].content if messages else ""
        # We include temperature in the response if it was passed, but it's not stored on self by default in BaseChatModel unless we define it.
        # BaseChatModel doesn't force a 'temperature' field. 
        # We can assume it might be in kwargs or we just ignore it for the mock string to match previous behavior approximately.
        response = f"Mock response from {self.model_name}: {last_msg}"
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=response))])
    
    @property
    def _llm_type(self) -> str:
        return "mock"

class ModelFactory:
    @staticmethod
    def create(provider: str, model: str, temperature: float = 0.7, **kwargs) -> BaseChatModel:
        """
        Creates a LangChain Chat Model based on the provider and configuration.
        """
        if provider.lower() == "openai":
            # Ensure api_key is handled by env var or kwargs
            return ChatOpenAI(model=model, temperature=temperature, **kwargs)
        elif provider.lower() == "ollama":
            return ChatOllama(model=model, temperature=temperature, **kwargs)
        elif provider.lower() == "mock":
            return MockChatModel(model_name=model, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
