import pytest
from wfir.runtime.nodes import LLMNode, LLMParams, NodeDef
from wfir.runtime.base import Context
from wfir.runtime.llm import ModelFactory, MockChatModel
from langchain_core.messages import HumanMessage

def test_model_factory_mock():
    client = ModelFactory.create("mock", "test-model")
    assert isinstance(client, MockChatModel)
    response = client.invoke([HumanMessage(content="Hello")])
    assert "Mock response from test-model" in response.content
    assert "Hello" in response.content

def test_llm_node_mock_execution():
    node = LLMNode()
    params = LLMParams(
        provider="mock",
        model="test-model",
        temperature=0.5,
        system_prompt="sys"
    )
    node_def = NodeDef(
        params=params,
        node_id="test-node"
    )
    
    inputs = {"prompt": "How are you?"}
    context = Context(initial_vars={})
    
    result = node.execute(inputs, context, node_def)
    
    assert "Mock response from test-model" in result
    assert "How are you?" in result

def test_llm_node_missing_prompt():
    node = LLMNode()
    params = LLMParams(provider="mock", model="test")
    node_def = NodeDef(params=params, node_id="n1")
    
    result = node.execute({}, Context(), node_def)
    assert "Error: 'prompt' input missing" in result
