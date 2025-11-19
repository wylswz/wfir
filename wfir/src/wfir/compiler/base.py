from abc import ABC, abstractmethod
from typing import Any
from wfir.models import WorkflowIR, Node, Edge

class IRVisitor(ABC):
    """
    Abstract base class for Workflow IR visitors.
    Follows the Visitor pattern to traverse the IR structure.
    """

    @abstractmethod
    def visit_workflow(self, workflow: WorkflowIR) -> Any:
        pass

    @abstractmethod
    def visit_node(self, node: Node) -> Any:
        pass

    @abstractmethod
    def visit_edge(self, edge: Edge) -> Any:
        pass

