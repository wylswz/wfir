from typing import Any, Dict, Optional, Protocol

class Context:
    """
    Runtime context for the workflow.
    Holds variables and state.
    """
    def __init__(self, initial_vars: Dict[str, Any] = None):
        self._store: Dict[str, Any] = initial_vars or {}
        self._node_outputs: Dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def set(self, key: str, value: Any):
        self._store[key] = value

    def get_node_output(self, node_id: str, key: str = "output") -> Any:
        outputs = self._node_outputs.get(node_id, {})
        if isinstance(outputs, dict):
            return outputs.get(key)
        return outputs if key == "output" else None

    def set_node_output(self, node_id: str, output: Any):
        self._node_outputs[node_id] = output
        # Optionally merge into main store if needed, but keeping separate is cleaner for IR logic

class WorkflowNode(Protocol):
    """Protocol that all generated/runtime nodes must implement."""
    def execute(self, inputs: Dict[str, Any], context: Context, node_def: Dict[str, Any] = None) -> Any:
        ...

