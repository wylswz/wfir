from typing import Dict, Set, List, Any
from collections import deque
from wfir.models import WorkflowIR, Node

class WorkflowVerifier:
    def __init__(self, workflow: WorkflowIR):
        self.workflow = workflow
        self.node_map = {n.id: n for n in self.workflow.nodes}
        self.adj_list: Dict[str, List[str]] = {n.id: [] for n in self.workflow.nodes}
        self.in_degree: Dict[str, int] = {n.id: 0 for n in self.workflow.nodes}
        
        for edge in self.workflow.edges:
            self.adj_list[edge.source].append(edge.target)
            self.in_degree[edge.target] += 1

    def verify(self) -> List[str]:
        """
        Verifies the workflow IR.
        Returns a list of error messages. Empty list means valid.
        """
        errors = []
        
        # 1. Check for Cycles (Basic DAG check)
        # Note: If we support Loop nodes, this check needs to be smarter (allow cycles involving Loop nodes)
        # For now, we assume a DAG for the main flow.
        if not self._is_dag():
            errors.append("Workflow contains cycles (loops), which are only allowed via specific Loop nodes (not yet implemented).")

        # 2. Data Flow Verification
        # Simulate execution to check if inputs are available when needed.
        data_errors = self._verify_data_flow()
        errors.extend(data_errors)

        # 3. Node Parameter Verification (e.g. Condition targets)
        param_errors = self._verify_node_params()
        errors.extend(param_errors)

        return errors

    def _verify_node_params(self) -> List[str]:
        errors = []
        for node in self.workflow.nodes:
            if node.type == "Condition":
                # Expect 'true_target' and 'false_target' in params
                targets = []
                if "true_target" in node.params:
                    targets.append(node.params["true_target"])
                if "false_target" in node.params:
                    targets.append(node.params["false_target"])
                
                if "targets" in node.params and isinstance(node.params["targets"], list):
                    targets.extend(node.params["targets"])

                for target_id in targets:
                    if target_id not in self.node_map:
                        errors.append(f"Condition Node '{node.id}' references non-existent target '{target_id}'")
                
                # Check condition definition
                if "expression" in node.params:
                    if not isinstance(node.params["expression"], str):
                         errors.append(f"Condition Node '{node.id}' has invalid 'expression' type (expected string)")
                else:
                    errors.append(f"Condition Node '{node.id}' missing 'expression' parameter")

        return errors

    def _is_dag(self) -> bool:
        """Standard Kahn's algorithm to check for cycles."""
        in_degree = self.in_degree.copy()
        queue = deque([n for n in self.node_map if in_degree[n] == 0])
        visited_count = 0
        
        while queue:
            u = queue.popleft()
            visited_count += 1
            
            for v in self.adj_list[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
                    
        return visited_count == len(self.workflow.nodes)

    def _verify_data_flow(self) -> List[str]:
        errors = []
        # Track available variables: "node_id.output_key" -> "Type"
        available_vars: Dict[str, str] = {}
        
        # Initialize with global variables if any
        # Assuming variables dict values are types or initial values. 
        # If values, we infer type. If types (as strings), we use them.
        for var_name, var_val in self.workflow.variables.items():
            # Simple heuristic: if it looks like a type name, use it, else infer
            var_type = "Any"
            if isinstance(var_val, str) and var_val[0].isupper():
                 var_type = var_val
            else:
                 var_type = type(var_val).__name__
            available_vars[f"global.{var_name}"] = var_type

        # Topological traversal for data flow
        in_degree = self.in_degree.copy()
        queue = deque([n for n in self.node_map if in_degree[n] == 0])
        
        # Also need to track which nodes have "executed" to provide their outputs
        executed_nodes = set()

        while queue:
            u_id = queue.popleft()
            node = self.node_map[u_id]
            executed_nodes.add(u_id)
            
            # Check inputs
            for input_name, input_val in node.inputs.items():
                if input_val.value_from:
                    ref_node = input_val.value_from.node_id
                    ref_key = input_val.value_from.output_key or "output"
                    ref_full = f"{ref_node}.{ref_key}"
                    
                    if ref_full not in available_vars:
                        # Check if it's a global variable reference (e.g. node_id="global")
                        if ref_node == "global":
                             if f"global.{ref_key}" not in available_vars:
                                  errors.append(f"Node '{u_id}' input '{input_name}' references missing global variable '{ref_key}'")
                        else:
                             errors.append(f"Node '{u_id}' input '{input_name}' references missing value '{ref_full}'")
                    else:
                        # Optional: Type Checking logic here
                        # expected_type = node.input_schema[input_name] (if we had it)
                        # actual_type = available_vars[ref_full]
                        pass

            # "Execute" node -> Produce outputs
            # We assume the node produces all keys defined in its 'outputs' field
            for out_key, out_type in node.outputs.items():
                available_vars[f"{u_id}.{out_key}"] = out_type

            # Continue traversal
            for v in self.adj_list[u_id]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
                    
        return errors

