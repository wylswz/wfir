# Workflow IR

Workflow IR serves as next generation workflow interface in AI era. There are bunch of workflow implementations available on the market, such as dify, rafglow, langgraph. However, they are not interoperatable. Workflow IR tries to define a common workflow representation to make workflows portable.

## What is Workflow IR

Workflow intermediate representation (WFIR) is an abstraction of workflow, which can be transpiled into concrete implementations. It represents the workflow as a Directed Graph (DAG or Cyclic) with explicit data flow.

Core concepts:
- **Nodes**: Functional units (Start, End, LLM, Tool, Condition, Loop).
- **Edges**: Control flow connections between nodes.
- **Inputs/Outputs**: Data passing between nodes via a shared Context.
- **Context**: Global and local state storage.

## IR Structure

The IR is a JSON object with the following structure:

```json
{
  "name": "My Workflow",
  "variables": {
    "user_name": "String",
    "history": "List[Message]"
  },
  "nodes": [
    {
      "id": "node-1",
      "type": "StartNode",
      "outputs": {"output": "String"}
    },
    {
      "id": "node-2",
      "type": "Condition",
      "params": {
        "expression": "input.val > 0.5",
        "true_target": "node-3",
        "false_target": "node-4"
      }
    }
  ],
  "edges": [
    {"source": "node-1", "target": "node-2"},
    {"source": "node-2", "target": "node-3"},
    {"source": "node-2", "target": "node-4"}
  ]
}
```

### Node Definition

Each node has:
- `id`: Unique identifier.
- `type`: FQDN or built-in type (e.g., `Condition`, `Loop`).
- `inputs`: Mapping of arguments to values or references (`valueFrom`).
- `outputs`: Schema of produced variables.
- `params`: Type-specific configuration (e.g., condition logic, loop body).
- `stream`: Boolean flag indicating if the node streams data.

### Control Flow

- **Edges**: Define the default execution path.
- **Condition Node**: Uses an expression language (like CEL) to decide the next step. The targets are defined in `params` and should match the graph edges.
- **Loop Node**: Defines a subgraph or a jump-back mechanism. It acts as a conditional router that evaluates an expression to decide whether to continue the loop (`body_target`) or exit (`end_target`).

### Data Flow

Data is passed via the Context. Nodes read from Context using `valueFrom` references:
```json
"inputs": {
  "query": {
    "valueFrom": {
      "nodeId": "node-1",
      "outputKey": "output"
    }
  }
}
```

## CLI Usage

WFIR provides a CLI to compile IR files to target platforms.

```bash
# Compile to LangGraph (default)
wfir compile ir.json > workflow.py

# Specify target
wfir compile ir.json --target=langgraph > workflow.py
```

## Standard Nodes

The Runtime Library provides implementations for standard nodes:

- **StartNode**: Entry point of the workflow.
- **EndNode**: Exit point of the workflow.
- **LLM**: Invokes a Large Language Model.
  - Inputs: `prompt`, `model` (optional)
- **HTTP**: Makes an HTTP request.
  - Inputs: `url`, `method` (optional)
- **Tool**: Executes a registered tool.
  - Inputs: `tool_name`, `tool_args` (optional)
- **Condition**: Evaluates an expression to determine control flow.
  - Params: `expression`, `true_target`, `false_target`
- **Loop**: Evaluates an expression to control loop execution.
  - Params: `expression`, `body_target` (or `true_target`), `end_target` (or `false_target`)

## Transpiler

The transpiler generates code for target platforms (LangGraph, Dify, etc.). It relies on a **Runtime Library** that provides implementations for the node types.

Example (LangGraph target):
```python
def generated_node(state: State):
    # Node definition is embedded for runtime context
    node_def = {
        "id": "node-1",
        "type": "StartNode",
        # ...
    }
    
    # Resolve inputs
    inputs = resolve_inputs(state, node_def)
    
    # Execute node logic via Runtime, passing the full node definition
    result = runtime.execute("NodeTypeName", inputs, node_def)
    
    # Update state
    return {"node_id_output": result}

def build_graph():
    workflow = StateGraph(AgentState)
    # ... add nodes and edges ...
    return workflow # Returns StateGraph, user calls .compile()
```

## Streaming

The IR defines `stream: bool`. The target platform is responsible for handling the actual streaming protocol (SSE, WebSocket, etc.) and event types.

## Human in the Loop

Workflows can be interrupted. This is modeled as a node that suspends execution until an external event (callback) provides the required input.
