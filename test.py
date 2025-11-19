from typing import TypedDict, Annotated, List, Dict, Union, Any
from langgraph.graph import StateGraph, END
from wfir.runtime.registry import Runtime
from wfir.runtime.base import Context

# Initialize Runtime
# In a real app, Context might need to be initialized per request/execution
runtime = Runtime()

# --- State Definition ---
class AgentState(TypedDict):
    """
    Global state for the workflow.
    """
    # Global variables defined in IR
    
    
    # Internal: Node outputs storage
    
    start_output: Any
    
    end_output: Any
    
    llm_1763533365295_output: Any
    

# --- Node Definitions ---

def start(state: AgentState):
    """
    Node ID: start
    Type: StartNode
    """
    print(f"--- Executing start ---")
    
    # Node Definition
    node_def = {"id": "start", "inputs": {}, "metadata": {"position": {"x": -32, "y": 39.5}}, "outputs": {"output": "String"}, "params": {}, "stream": false, "type": "StartNode"}

    # Resolve Inputs
    inputs = {}
    
    
    # Add params to inputs (merged)
    

    # Execute Logic
    try:
        result = runtime.execute("StartNode", inputs, node_def)
    except Exception as e:
        print(f"Error executing node start: {e}")
        raise e
    
    # Return updates to state
    return {"start_output": result}

def end(state: AgentState):
    """
    Node ID: end
    Type: EndNode
    """
    print(f"--- Executing end ---")
    
    # Node Definition
    node_def = {"id": "end", "inputs": {"value": {"value": null, "valueFrom": {"nodeId": "start", "outputKey": "output"}}}, "metadata": {"position": {"x": 73.5, "y": 244.5}}, "outputs": {"output": "Any"}, "params": {}, "stream": false, "type": "EndNode"}

    # Resolve Inputs
    inputs = {}
    
    
    # Reference: start.output
    source_output = state.get("start_output")
    if isinstance(source_output, dict):
        inputs["value"] = source_output.get("output")
    else:
        inputs["value"] = source_output
    
    
    
    # Add params to inputs (merged)
    

    # Execute Logic
    try:
        result = runtime.execute("EndNode", inputs, node_def)
    except Exception as e:
        print(f"Error executing node end: {e}")
        raise e
    
    # Return updates to state
    return {"end_output": result}

def llm_1763533365295(state: AgentState):
    """
    Node ID: llm-1763533365295
    Type: LLM
    """
    print(f"--- Executing llm-1763533365295 ---")
    
    # Node Definition
    node_def = {"id": "llm-1763533365295", "inputs": {"prompt": {"value": "Hello world", "valueFrom": null}}, "metadata": {"position": {"x": 51, "y": 119}}, "outputs": {"output": "Any"}, "params": {"model": "gpt-4-turbo", "system_prompt": null, "temperature": 1}, "stream": false, "type": "LLM"}

    # Resolve Inputs
    inputs = {}
    
    
    # Literal value
    inputs["prompt"] = "Hello world"
    
    
    
    # Add params to inputs (merged)
    
    inputs["model"] = "gpt-4-turbo"
    
    inputs["temperature"] = 1
    
    inputs["system_prompt"] = null
    

    # Execute Logic
    try:
        result = runtime.execute("LLM", inputs, node_def)
    except Exception as e:
        print(f"Error executing node llm-1763533365295: {e}")
        raise e
    
    # Return updates to state
    return {"llm_1763533365295_output": result}


# --- Graph Construction ---
def build_graph():
    workflow = StateGraph(AgentState)

    # 1. Add Nodes
    
    workflow.add_node("start", start)
    
    workflow.add_node("end", end)
    
    workflow.add_node("llm-1763533365295", llm_1763533365295)
    

    # 2. Add Edges
    
    workflow.add_edge("start", "llm-1763533365295")
    
    workflow.add_edge("llm-1763533365295", "end")
    

    # 3. Set Entry Point
    # Assuming the first node in the list is the start, or we need explicit start
    
    workflow.set_entry_point("start")
    

    return workflow

if __name__ == "__main__":
    app = build_graph().compile()
    print("Graph compiled successfully.")
    print(app.get_graph().draw_ascii())
    app.invoke({"start": "Hello world"})