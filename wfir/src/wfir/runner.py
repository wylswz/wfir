import asyncio
from typing import Dict, Any, Callable, Awaitable
from wfir.models import WorkflowIR, Node

# Type for a node handler function
# It takes (inputs, context, node_def) and returns output
NodeHandler = Callable[[Dict[str, Any], Dict[str, Any], Dict[str, Any]], Awaitable[Any]]

class WorkflowRunner:
    def __init__(self, workflow: WorkflowIR):
        self.workflow = workflow
        self.handlers: Dict[str, NodeHandler] = {}
        self.context: Dict[str, Any] = workflow.variables.copy()
        self.node_outputs: Dict[str, Any] = {}

    def register_handler(self, node_type: str, handler: NodeHandler):
        """Register a python function to handle a specific node type."""
        self.handlers[node_type] = handler

    async def _resolve_inputs(self, node: Node) -> Dict[str, Any]:
        resolved = {}
        for name, input_val in node.inputs.items():
            if input_val.value is not None:
                resolved[name] = input_val.value
            elif input_val.value_from:
                ref_node_id = input_val.value_from.node_id
                
                if ref_node_id not in self.node_outputs:
                    raise RuntimeError(f"Node '{node.id}' depends on '{ref_node_id}' which has not executed yet.")
                
                output = self.node_outputs[ref_node_id]
                resolved[name] = output
        return resolved

    async def run(self, start_inputs: Dict[str, Any] = None):
        """
        Simple topological execution. 
        For a real runner, we'd build a DAG and execute ready nodes.
        Here we just iterate linearly for the demo since our test case is linear.
        """
        if start_inputs:
            self.context.update(start_inputs)

        # 1. Build Adjacency Map to find start nodes (nodes with no incoming edges)
        # For this simple version, we will just iterate through the list order 
        # assuming the user provided a topologically sorted list or we just find the start node.
        # A real runner needs a proper graph traversal (BFS/DFS).
        
        # Let's just execute in the order they appear in the list for this MVP
        # assuming the list is sorted.
        
        print(f"--- Starting Workflow: {self.workflow.name} ---")
        
        for node in self.workflow.nodes:
            print(f"Executing Node: {node.id} ({node.type})")
            
            # 1. Resolve Inputs
            inputs = await self._resolve_inputs(node)
            
            # 2. Find Handler
            handler = self.handlers.get(node.type)
            if not handler:
                print(f"  Warning: No handler for type '{node.type}'. Skipping.")
                continue
            
            # 3. Execute
            try:
                # Pass node definition (as dict) to handler
                # node.model_dump() converts the pydantic model to a dict
                node_def = node.model_dump(by_alias=True)
                output = await handler(inputs, self.context, node_def)
                self.node_outputs[node.id] = output
                print(f"  Output: {output}")
                
                # Update context if needed (optional design choice)
                # self.context[f"{node.id}.output"] = output
                
            except Exception as e:
                print(f"  Error executing node {node.id}: {e}")
                raise e
                
        print("--- Workflow Completed ---")
        return self.node_outputs
