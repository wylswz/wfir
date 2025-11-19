from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from wfir.models import WorkflowIR
from wfir.compiler.langgraph.transpiler import LangGraphTranspiler
from wfir.runtime.registry import NodeRegistry

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/node-types")
async def get_node_types():
    return NodeRegistry.get_all_schemas()

@app.post("/validate")
async def validate_workflow(workflow: WorkflowIR):
    """
    Validates the workflow IR.
    """
    try:
        # Static validation is already done by Pydantic model (WorkflowIR)
        # We can add additional semantic validation here if needed
        # For example, checking if all node types exist in registry
        
        unknown_types = []
        for node in workflow.nodes:
            try:
                NodeRegistry.get(node.type)
            except ValueError:
                unknown_types.append(f"Node '{node.id}' has unknown type '{node.type}'")
        
        if unknown_types:
            return {"valid": False, "errors": unknown_types}

        return {"valid": True, "errors": []}
    except Exception as e:
        return {"valid": False, "errors": [str(e)]}

class CompileRequest(BaseModel):
    workflow: WorkflowIR
    target: str = "langgraph"

@app.post("/compile")
async def compile_workflow(request: CompileRequest):
    """
    Compiles the workflow IR to the target language/framework.
    """
    if request.target == "langgraph":
        transpiler = LangGraphTranspiler()
        try:
            code = transpiler.visit_workflow(request.workflow)
            return {"code": code}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Compilation failed: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported target: {request.target}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
