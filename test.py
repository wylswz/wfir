import json
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
    
    llm_1763542362909_output: Any
    
    llm_1763542969691_output: Any
    

# --- Node Definitions ---

def start(state: AgentState):
    """
    Node ID: start
    Type: StartNode
    """
    print(f"--- Executing start ---")
    
    # Node Definition
    node_def = json.loads("""{
  "id": "start",
  "type": "StartNode",
  "inputs": {},
  "outputs": {
    "output": "Any"
  },
  "params": {},
  "stream": false,
  "metadata": {
    "position": {
      "x": 100,
      "y": 100
    }
  }
}""")

    # Initialize Context
    context = Context(state)

    # Resolve Inputs
    inputs = context.resolve_inputs(node_def.get("inputs", {}))
    
    # Execute Logic
    try:
        # Pass context to execute
        result = runtime.execute("StartNode", inputs, context, node_def)
    except Exception as e:
        print(f"Error executing node start: {e}")
        raise e
    
    # Set Output in Context
    context.set_node_output("start", result)

    # Return updates to state
    # We explicitly return the output update to satisfy LangGraph contract
    return {"start_output": result}

def end(state: AgentState):
    """
    Node ID: end
    Type: EndNode
    """
    print(f"--- Executing end ---")
    
    # Node Definition
    node_def = json.loads("""{
  "id": "end",
  "type": "EndNode",
  "inputs": {},
  "outputs": {
    "output": "Any"
  },
  "params": {},
  "stream": false,
  "metadata": {
    "position": {
      "x": 137,
      "y": 364
    }
  }
}""")

    # Initialize Context
    context = Context(state)

    # Resolve Inputs
    inputs = context.resolve_inputs(node_def.get("inputs", {}))
    
    # Execute Logic
    try:
        # Pass context to execute
        result = runtime.execute("EndNode", inputs, context, node_def)
    except Exception as e:
        print(f"Error executing node end: {e}")
        raise e
    
    # Set Output in Context
    context.set_node_output("end", result)

    # Return updates to state
    # We explicitly return the output update to satisfy LangGraph contract
    return {"end_output": result}

def llm_1763542362909(state: AgentState):
    """
    Node ID: llm-1763542362909
    Type: LLM
    """
    print(f"--- Executing llm-1763542362909 ---")
    
    # Node Definition
    node_def = json.loads("""{
  "id": "llm-1763542362909",
  "type": "LLM",
  "inputs": {
    "prompt": {
      "value": "hello",
      "valueFrom": null
    }
  },
  "outputs": {
    "output": "Any"
  },
  "params": {
    "provider": "openai",
    "model": "gpt-4o",
    "temperature": 0.7,
    "system_prompt": ""
  },
  "stream": false,
  "metadata": {
    "position": {
      "x": 219.50086212158203,
      "y": 166.23263549804688
    }
  }
}""")

    # Initialize Context
    context = Context(state)

    # Resolve Inputs
    inputs = context.resolve_inputs(node_def.get("inputs", {}))
    
    # Execute Logic
    try:
        # Pass context to execute
        result = runtime.execute("LLM", inputs, context, node_def)
    except Exception as e:
        print(f"Error executing node llm-1763542362909: {e}")
        raise e
    
    # Set Output in Context
    context.set_node_output("llm-1763542362909", result)

    # Return updates to state
    # We explicitly return the output update to satisfy LangGraph contract
    return {"llm_1763542362909_output": result}

def llm_1763542969691(state: AgentState):
    """
    Node ID: llm-1763542969691
    Type: LLM
    """
    print(f"--- Executing llm-1763542969691 ---")
    
    # Node Definition
    node_def = json.loads("""{
  "id": "llm-1763542969691",
  "type": "LLM",
  "inputs": {
    "prompt": {
      "value": null,
      "valueFrom": {
        "nodeId": "llm-1763542362909"
      }
    }
  },
  "outputs": {
    "output": "Any"
  },
  "params": {
    "provider": "openai",
    "model": "gpt-4o",
    "temperature": 0.7,
    "system_prompt": ""
  },
  "stream": false,
  "metadata": {
    "position": {
      "x": 193.25129318237305,
      "y": 274.2326354980469
    }
  }
}""")

    # Initialize Context
    context = Context(state)

    # Resolve Inputs
    inputs = context.resolve_inputs(node_def.get("inputs", {}))
    
    # Execute Logic
    try:
        # Pass context to execute
        result = runtime.execute("LLM", inputs, context, node_def)
    except Exception as e:
        print(f"Error executing node llm-1763542969691: {e}")
        raise e
    
    # Set Output in Context
    context.set_node_output("llm-1763542969691", result)

    # Return updates to state
    # We explicitly return the output update to satisfy LangGraph contract
    return {"llm_1763542969691_output": result}


# --- Graph Construction ---
def build_graph():
    workflow = StateGraph(AgentState)

    # 1. Add Nodes
    
    workflow.add_node("start", start)
    
    workflow.add_node("end", end)
    
    workflow.add_node("llm-1763542362909", llm_1763542362909)
    
    workflow.add_node("llm-1763542969691", llm_1763542969691)
    

    # 2. Add Edges
    
    workflow.add_edge("start", "llm-1763542362909")
    
    workflow.add_edge("llm-1763542362909", "llm-1763542969691")
    
    workflow.add_edge("llm-1763542969691", "end")
    

    # 3. Set Entry Point
    # Assuming the first node in the list is the start, or we need explicit start
    
    workflow.set_entry_point("start")
    

    return workflow

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "1"}}
    from langgraph.checkpoint.memory import MemorySaver
    app = build_graph().compile(checkpointer=MemorySaver())
    print("Graph compiled successfully.")
    app.invoke({}, config)
    print(app.get_state(config))