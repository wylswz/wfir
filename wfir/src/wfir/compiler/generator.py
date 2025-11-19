import os
from jinja2 import Environment, FileSystemLoader
from wfir.models import WorkflowIR

class Compiler:
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader(template_dir))
    
    def compile(self, workflow: WorkflowIR) -> str:
        template = self.env.get_template("workflow.py.j2")
        
        # We need to pass the nodes in topological order for the linear execution script to work.
        # For now, we assume the IR nodes list is already sorted or we just use it as is.
        # A real compiler would perform topological sort here.
        
        return template.render(nodes=workflow.nodes, workflow=workflow)

    def compile_to_file(self, workflow: WorkflowIR, output_path: str):
        code = self.compile(workflow)
        with open(output_path, "w") as f:
            f.write(code)
        print(f"Compiled workflow '{workflow.name}' to {output_path}")

