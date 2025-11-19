from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field, model_validator

# --- Value Definitions ---

class ValueFrom(BaseModel):
    """Reference to an output from another node."""
    node_id: str = Field(..., alias="nodeId")
    output_key: Optional[str] = Field(default="output", alias="outputKey")

class InputValue(BaseModel):
    """Represents an input value which can be static or a reference."""
    value: Optional[Any] = None
    value_from: Optional[ValueFrom] = Field(None, alias="valueFrom")

    @model_validator(mode='after')
    def check_value_or_ref(self):
        if self.value is None and self.value_from is None:
            # It's possible to have optional inputs, but if defined, usually one is needed.
            # For now, we allow empty for optional inputs, but in strict mode we might enforce one.
            pass
        if self.value is not None and self.value_from is not None:
            raise ValueError("Cannot specify both 'value' and 'valueFrom'")
        return self

# --- Node Definitions ---

class Node(BaseModel):
    """Base definition of a workflow node."""
    id: str
    type: str
    # Inputs are a map of argument name -> InputValue
    inputs: Dict[str, InputValue] = Field(default_factory=dict)
    
    # Expected outputs (name -> type/description)
    outputs: Dict[str, str] = Field(default_factory=lambda: {"output": "Any"})
    
    # Type-specific parameters (e.g. condition logic, loop configuration)
    params: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata for execution
    stream: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

# --- Edge Definitions ---

class Edge(BaseModel):
    """Defines a connection between two nodes."""
    source: str
    target: str
    # Optional handles if nodes have multiple ports
    source_handle: Optional[str] = Field(None, alias="sourceHandle")
    target_handle: Optional[str] = Field(None, alias="targetHandle")
    
    # Conditional logic for traversing this edge
    condition: Optional[str] = None

# --- Workflow Definition ---

class WorkflowIR(BaseModel):
    """The root object representing the Workflow Intermediate Representation."""
    version: str = "0.1.0"
    name: str
    nodes: List[Node]
    edges: List[Edge]
    
    # Global variables / Context schema could go here
    variables: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode='after')
    def validate_edges(self):
        """Ensure all edges point to existing nodes."""
        node_ids = {n.id for n in self.nodes}
        for edge in self.edges:
            if edge.source not in node_ids:
                raise ValueError(f"Edge source '{edge.source}' does not exist in nodes.")
            if edge.target not in node_ids:
                raise ValueError(f"Edge target '{edge.target}' does not exist in nodes.")
        return self

