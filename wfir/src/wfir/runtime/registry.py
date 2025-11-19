from typing import Dict, Type, Any
from wfir.runtime.base import Context
from wfir.runtime.nodes import NodeImplementation, StartNode, EndNode, LLMNode, HTTPNode, ToolNode, ConditionNode, LoopNode, NodeDef

class NodeRegistry:
    _registry: Dict[str, Type[NodeImplementation]] = {
        "StartNode": StartNode,
        "EndNode": EndNode,
        "LLM": LLMNode,
        "HTTP": HTTPNode,
        "Tool": ToolNode,
        "Condition": ConditionNode,
        "Loop": LoopNode,
    }

    @classmethod
    def register(cls, name: str, node_cls: Type[NodeImplementation]):
        cls._registry[name] = node_cls

    @classmethod
    def get(cls, name: str) -> NodeImplementation:
        node_cls = cls._registry.get(name)
        if not node_cls:
            raise ValueError(f"Node type '{name}' not found in registry.")
        return node_cls()

    @classmethod
    def get_all_schemas(cls) -> Dict[str, Any]:
        schemas = {}
        for name, node_cls in cls._registry.items():
            if node_cls.params_model:
                schemas[name] = node_cls.params_model.model_json_schema()
            else:
                schemas[name] = {}
        return schemas

class Runtime:
    def __init__(self, context: Context = None):
        self.context = context or Context()

    def execute(self, node_type: str, inputs: Dict[str, Any], node_def: Dict[str, Any] = None) -> Any:
        node_impl = NodeRegistry.get(node_type)
        
        # Create NodeDef from dict
        raw_params = node_def.get("params", {}) if node_def else {}
        validated_params = node_impl.params_model(**raw_params)
        
        node_id = node_def.get("id") if node_def else "unknown"
        
        node_def_obj = NodeDef(
            params=validated_params,
            node_id=node_id
        )
        
        return node_impl.execute(inputs, self.context, node_def_obj)
