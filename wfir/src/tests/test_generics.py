import pytest
from wfir.runtime.nodes import LLMNode, LLMParams, HTTPNode, HTTPParams, NodeImplementation, StartNode, EmptyParams

def test_node_generics():
    # Verify that LLMNode has the correct params_model
    assert LLMNode.params_model == LLMParams
    assert issubclass(LLMNode, NodeImplementation)
    
    # Instantiate and check
    node = LLMNode()
    assert node.params_model == LLMParams

    # Check schema generation
    schema = LLMNode.params_model.model_json_schema()
    assert "properties" in schema
    assert "model" in schema["properties"]
    assert "temperature" in schema["properties"]

def test_start_node_generics():
    # StartNode uses EmptyParams default
    assert StartNode.params_model == EmptyParams
    schema = StartNode.params_model.model_json_schema()
    assert "properties" in schema
    # EmptyParams should have no properties (or empty properties)
    assert len(schema.get("properties", {})) == 0

def test_registry_integration():
    from wfir.runtime.registry import NodeRegistry
    
    schemas = NodeRegistry.get_all_schemas()
    assert "LLM" in schemas
    assert "HTTP" in schemas
    
    llm_schema = schemas["LLM"]
    assert llm_schema["properties"]["model"]["default"] == "gpt-3.5-turbo"
