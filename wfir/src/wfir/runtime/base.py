from typing import Any, Dict, Protocol, Optional

class Context:
    """
    Runtime context for the workflow.
    Wraps the state dictionary to provide helper methods.
    """
    def __init__(self, state: Dict[str, Any]):
        self._state = state

    def get(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def set(self, key: str, value: Any):
        self._state[key] = value

    def get_node_output(self, node_id: str) -> Any:
        """
        Retrieve the output of a specific node from the state.
        """
        sanitized_id = node_id.replace("-", "_")
        state_key = f"{sanitized_id}_output"
        return self._state.get(state_key)

    def set_node_output(self, node_id: str, value: Any):
        """
        Set the output of a specific node in the state.
        """
        sanitized_id = node_id.replace("-", "_")
        state_key = f"{sanitized_id}_output"
        self._state[state_key] = value

    def resolve_inputs(self, inputs_def: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolves input values from the node definition.
        Handles literal values and references to other nodes.
        """
        resolved = {}
        for name, input_val in inputs_def.items():
            # input_val is a dict (from model_dump, likely aliased)
            # structure: { value: ..., valueFrom: { nodeId: ... } }
            
            # Check for valueFrom (Reference)
            # Note: keys might be camelCase due to by_alias=True in template
            
            value_from = input_val.get("valueFrom")
            value = input_val.get("value")
            print(f"Value: {value}")
            print(f"Value from: {value_from}")
            
            if value_from:
                # Reference
                ref_node = value_from.get("nodeId")
                print(f"Ref node: {ref_node}")
                if ref_node:
                    # Get the entire output of the referenced node
                    resolved[name] = self.get_node_output(ref_node)
                else:
                    # Invalid reference
                    resolved[name] = None
            
            elif value is not None:
                # Literal value
                resolved[name] = value
            else:
                # No value provided
                resolved[name] = None
                
        return resolved

class WorkflowNode(Protocol):
    """Protocol that all generated/runtime nodes must implement."""
    def execute(self, inputs: Dict[str, Any], context: Context, node_def: Dict[str, Any] = None) -> Any:
        ...
