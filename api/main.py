from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import uuid
from wfir.models import WorkflowIR
from wfir.runner import WorkflowRunner
from wfir.compiler.langgraph.transpiler import LangGraphTranspiler
from wfir.runtime.registry import NodeRegistry
from wfir.runtime.nodes import NodeDef

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
workflows: Dict[str, WorkflowIR] = {}

# Add a sample workflow
sample_workflow = WorkflowIR(
    name="Sample Workflow",
    nodes=[
        {
            "id": "start",
            "type": "StartNode",
            "outputs": {"output": "String"}
        },
        {
            "id": "end",
            "type": "EndNode",
            "inputs": {
                "value": {
                    "valueFrom": {
                        "nodeId": "start",
                        "outputKey": "output"
                    }
                }
            }
        }
    ],
    edges=[
        {"source": "start", "target": "end"}
    ]
)
workflows["sample"] = sample_workflow

@app.get("/node-types")
async def get_node_types():
    return NodeRegistry.get_all_schemas()

@app.get("/workflows")
async def list_workflows():
    return [{"id": k, "name": v.name} for k, v in workflows.items()]

@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflows[workflow_id]

@app.post("/workflows")
async def create_workflow(workflow: WorkflowIR):
    workflow_id = str(uuid.uuid4())
    workflows[workflow_id] = workflow
    return {"id": workflow_id, "name": workflow.name}

@app.put("/workflows/{workflow_id}")
async def update_workflow(workflow_id: str, workflow: WorkflowIR):
    workflows[workflow_id] = workflow
    return {"id": workflow_id, "name": workflow.name}

class RunRequest(BaseModel):
    inputs: Dict[str, Any] = {}

@app.post("/workflows/{workflow_id}/run")
async def run_workflow(workflow_id: str, request: RunRequest):
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows[workflow_id]
    runner = WorkflowRunner(workflow)
    
    # Register handlers from NodeRegistry
    # We need to verify which node types are used in the workflow, 
    # or just register all available in registry.
    # Registry doesn't expose a list of keys easily unless we call get_all_schemas or access private dict.
    # But we can iterate over the workflow nodes and register what we need.
    
    unique_types = {node.type for node in workflow.nodes}
    
    for node_type in unique_types:
        try:
            # Validate it exists in registry
            NodeRegistry.get(node_type) 
            
            # Define async wrapper
            # We use a closure to capture node_type correctly
            def make_handler(nt: str):
                async def handler(inputs, context, node_dict: Dict[str, Any]):
                    impl = NodeRegistry.get(nt)
                    
                    # Validate params
                    raw_params = node_dict.get("params", {})
                    validated_params = impl.params_model(**raw_params)
                    
                    # Create NodeDef
                    node_def_obj = NodeDef(
                        params=validated_params,
                        node_id=node_dict.get("id")
                    )
                    
                    return impl.execute(inputs, context, node_def_obj)
                return handler
            
            runner.register_handler(node_type, make_handler(node_type))
            
        except ValueError:
            # Fallback for unknown types? Or let it fail in runner?
            print(f"Warning: Unknown node type '{node_type}'")
            # Register a dummy to avoid crash if that's preferred, or let it crash.
            pass

    try:
        outputs = await runner.run(request.inputs)
        return outputs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflows/{workflow_id}/transpile")
async def transpile_workflow(workflow_id: str, target: str = "langgraph"):
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows[workflow_id]
    
    if target == "langgraph":
        transpiler = LangGraphTranspiler()
        try:
            code = transpiler.visit_workflow(workflow)
            return {"code": code}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Transpilation failed: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported target: {target}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
