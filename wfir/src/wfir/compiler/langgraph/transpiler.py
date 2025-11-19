import os
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader
from wfir.models import WorkflowIR, Node, Edge
from wfir.compiler.base import IRVisitor

class LangGraphTranspiler(IRVisitor):
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.env.filters["repr"] = repr
        
        self.node_definitions: List[str] = []
        self.edge_definitions: List[str] = []
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self.variables: Dict[str, str] = {}
        self.start_node_id: str = ""

    def _map_type(self, wfir_type: str) -> str:
        type_map = {
            "String": "str",
            "Integer": "int",
            "Boolean": "bool",
            "Float": "float",
            "List": "List",
            "Dict": "Dict",
            "Any": "Any",
        }
        # Handle generics like List[Message]
        if "[" in wfir_type:
            base, inner = wfir_type.split("[", 1)
            inner = inner.rstrip("]")
            return f"{type_map.get(base, base)}[{self._map_type(inner)}]"
        
        return type_map.get(wfir_type, "Any")

    def visit_workflow(self, workflow: WorkflowIR) -> str:
        self.nodes = workflow.nodes
        self.edges = workflow.edges
        self.variables = {k: self._map_type(str(v)) for k, v in workflow.variables.items()}
        
        if self.nodes:
            self.start_node_id = self.nodes[0].id # Naive assumption for now

        # 1. Visit Nodes to generate definitions
        for node in self.nodes:
            self.visit_node(node)

        # 2. Visit Edges to generate connections
        # We need to handle Condition nodes specially here or in visit_node.
        # In LangGraph, edges are added to the graph.
        
        # Group edges by source to handle conditional logic if needed
        # But our IR has explicit Condition nodes.
        # If Node A -> Node B, we generate workflow.add_edge("A", "B")
        # If Node C (Condition) -> Node D (True) / Node E (False)
        # We need to generate add_conditional_edges("C", routing_function, path_map)
        
        # Let's process edges.
        # First, identify Condition nodes.
        condition_nodes = {n.id: n for n in self.nodes if n.type in ["Condition", "Loop"]}
        
        # Standard edges (Source is NOT a condition node)
        for edge in self.edges:
            if edge.source not in condition_nodes:
                # Standard edge
                # Check if target is a condition node? No, that's fine.
                self.edge_definitions.append(f'workflow.add_edge("{edge.source}", "{edge.target}")')

        # Conditional edges (Source IS a condition node)
        # We need to group outgoing edges from a condition node.
        for cond_id, cond_node in condition_nodes.items():
            # Find edges starting from this condition node
            outgoing = [e for e in self.edges if e.source == cond_id]
            
            # In LangGraph, a conditional edge usually requires a routing function.
            # Since we mapped Condition Node to a python function (in visit_node),
            # that function should return the destination node name (or a value we map).
            
            # Strategy: The Condition Node function returns the ID of the next node.
            # Then we use add_conditional_edges(cond_id, lambda x: x, path_map)
            
            path_map = {e.target: e.target for e in outgoing}
            # We need to know which edge corresponds to "true" or "false" if the condition logic returns boolean.
            # But our Condition Node logic (in IR params) defines targets.
            # If the generated python function for Condition Node returns the *Target Node ID*,
            # then the routing logic is simple.
            
            # Let's assume visit_node for Condition generates code that returns the target ID.
            
            mapping_str = ", ".join([f'"{tgt}": "{tgt}"' for tgt in path_map.keys()])
            self.edge_definitions.append(
                f'workflow.add_conditional_edges("{cond_id}", lambda x: x["{cond_id.replace("-", "_")}_output"], {{{mapping_str}}})'
            )

        # 3. Render Workflow
        template = self.env.get_template("workflow.py.j2")
        return template.render(
            variables=self.variables,
            nodes=self.nodes,
            node_definitions=self.node_definitions,
            edge_definitions=self.edge_definitions,
            start_node_id=self.start_node_id
        )

    def visit_node(self, node: Node) -> Any:
        node_func_name = node.id.replace("-", "_")
        
        # Use standard template for all nodes, including Condition and Loop
        # The runtime implementation will handle the logic and return the next node ID
        template = self.env.get_template("node.py.j2")
        code = template.render(node=node, node_func_name=node_func_name)
        self.node_definitions.append(code)

    def visit_edge(self, edge: Edge) -> Any:
        # Handled in visit_workflow for global graph construction
        pass
