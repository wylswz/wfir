import json
import pytest
from wfir.models import WorkflowIR
from wfir.compiler.langgraph.transpiler import LangGraphTranspiler
from wfir.runtime.registry import Runtime

def test_compile_and_run_simple_workflow():
    # Define a simple workflow
    ir_data = {
        "name": "Test Workflow",
        "variables": {
            "user_name": "String"
        },
        "nodes": [
            {
                "id": "start",
                "type": "StartNode",
                "outputs": {"output": "String"},
                "inputs": {"val": {"value": "Hello"}}
            },
            {
                "id": "end",
                "type": "EndNode",
                "outputs": {"output": "String"},
                "inputs": {
                    "final_val": {
                        "valueFrom": {
                            "nodeId": "start",
                            "outputKey": "output"
                        }
                    }
                }
            }
        ],
        "edges": [
            {"source": "start", "target": "end"}
        ]
    }

    workflow = WorkflowIR(**ir_data)
    transpiler = LangGraphTranspiler()
    code = transpiler.visit_workflow(workflow)

    # Verify code contains expected parts
    assert "class AgentState(TypedDict):" in code
    assert "def start(state: AgentState):" in code
    assert "def end(state: AgentState):" in code
    assert 'workflow.add_edge("start", "end")' in code
    assert 'node_def = {' in code # Check for node definition embedding

    # Execute the generated code
    # We need to mock the environment slightly or just exec it
    # Since the generated code imports from wfir, it should work if wfir is installed
    
    # Create a local scope for execution
    scope = {}
    try:
        exec(code, scope)
    except Exception as e:
        print(code) # Print code for debugging
        pytest.fail(f"Generated code failed to execute: {e}")

    # Check if build_graph function exists
    assert "build_graph" in scope
    build_graph = scope["build_graph"]
    
    # Run the graph
    # build_graph now returns StateGraph, so we need to compile it
    try:
        graph = build_graph()
        app = graph.compile()
    except Exception as e:
        pytest.fail(f"Failed to compile graph: {e}")

def test_compile_condition_workflow():
    ir_data = {
        "name": "Condition Workflow",
        "variables": {"val": "Integer"},
        "nodes": [
            {"id": "start", "type": "StartNode", "outputs": {"output": "Integer"}, "inputs": {"val": {"value": 10}}},
            {
                "id": "check", 
                "type": "Condition", 
                "params": {
                    "expression": "input['val'] > 5",
                    "true_target": "end_true",
                    "false_target": "end_false"
                },
                "inputs": {
                    "val": {"valueFrom": {"nodeId": "start", "outputKey": "output"}}
                }
            },
            {"id": "end_true", "type": "EndNode"},
            {"id": "end_false", "type": "EndNode"}
        ],
        "edges": [
            {"source": "start", "target": "check"},
            {"source": "check", "target": "end_true"},
            {"source": "check", "target": "end_false"}
        ]
    }
    
    workflow = WorkflowIR(**ir_data)
    transpiler = LangGraphTranspiler()
    code = transpiler.visit_workflow(workflow)
    
    assert 'workflow.add_conditional_edges("check"' in code
    
    scope = {}
    try:
        exec(code, scope)
    except Exception as e:
        print(code)
        pytest.fail(f"Generated code failed to execute: {e}")
        
    build_graph = scope["build_graph"]
    try:
        graph = build_graph()
        app = graph.compile()
    except Exception as e:
        pytest.fail(f"Failed to compile graph: {e}")

def test_compile_loop_workflow():
    ir_data = {
        "name": "Loop Workflow",
        "variables": {"count": "Integer"},
        "nodes": [
            {"id": "start", "type": "StartNode", "inputs": {"count": {"value": 0}}},
            {
                "id": "loop_check", 
                "type": "Loop", 
                "params": {
                    "expression": "input['count'] < 3",
                    "body_target": "increment",
                    "end_target": "end"
                },
                "inputs": {
                    "count": {"valueFrom": {"nodeId": "start", "outputKey": "output"}} # Mocking input flow
                }
            },
            {"id": "increment", "type": "EndNode"}, # Mock body
            {"id": "end", "type": "EndNode"}
        ],
        "edges": [
            {"source": "start", "target": "loop_check"},
            {"source": "loop_check", "target": "increment"},
            {"source": "loop_check", "target": "end"}
        ]
    }
    
    workflow = WorkflowIR(**ir_data)
    transpiler = LangGraphTranspiler()
    code = transpiler.visit_workflow(workflow)
    
    assert 'workflow.add_conditional_edges("loop_check"' in code
    
    scope = {}
    try:
        exec(code, scope)
    except Exception as e:
        print(code)
        pytest.fail(f"Generated code failed to execute: {e}")
        
    build_graph = scope["build_graph"]
    try:
        graph = build_graph()
        app = graph.compile()
    except Exception as e:
        pytest.fail(f"Failed to compile graph: {e}")
