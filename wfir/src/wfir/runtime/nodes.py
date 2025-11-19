from typing import Any, Dict, Optional, Type, TypeVar, Generic
from pydantic import BaseModel, Field
from wfir.runtime.base import Context

class EmptyParams(BaseModel):
    pass

TParams = TypeVar("TParams", bound=BaseModel)

class NodeDef(BaseModel, Generic[TParams]):
    params: TParams
    node_id: str
    

class NodeImplementation(Generic[TParams]):
    params_model: Type[TParams] = EmptyParams

    def execute(self, inputs: Dict[str, Any], context: Context, node_def: NodeDef[TParams]) -> Any:
        raise NotImplementedError

class StartNode(NodeImplementation[EmptyParams]):
    def execute(self, inputs: Dict[str, Any], context: Context, node_def: NodeDef[EmptyParams]) -> Any:
        # StartNode usually just passes through initial inputs or does nothing
        return inputs

class EndNode(NodeImplementation[EmptyParams]):
    def execute(self, inputs: Dict[str, Any], context: Context, node_def: NodeDef[EmptyParams]) -> Any:
        return inputs

class LLMParams(BaseModel):
    provider: str = Field("openai", description="The model provider (e.g. openai, mock)")
    model: str = Field("gpt-3.5-turbo", description="The LLM model to use")
    temperature: float = Field(0.7, description="Sampling temperature", ge=0.0, le=2.0)
    system_prompt: str = Field("", description="System prompt")

class LLMNode(NodeImplementation[LLMParams]):
    params_model = LLMParams

    def execute(self, inputs: Dict[str, Any], context: Context, node_def: NodeDef[LLMParams]) -> Any:
        prompt = inputs.get("prompt")
        if prompt is None:
            # Try to find 'input' if prompt is not explicit, as a fallback convention? 
            # Or just return error/empty. 
            # Based on existing code: prompt = inputs.get("prompt")
            return "Error: 'prompt' input missing"

        params = node_def.params
        
        from wfir.runtime.llm import ModelFactory
        from langchain_core.messages import HumanMessage, SystemMessage
        
        try:
            model = ModelFactory.create(
                provider=params.provider,
                model=params.model,
                temperature=params.temperature
            )
            
            messages = []
            if params.system_prompt:
                messages.append(SystemMessage(content=params.system_prompt))
            messages.append(HumanMessage(content=str(prompt)))
            
            response = model.invoke(messages)
            return response.content
        except Exception as e:
            return f"Error executing LLMNode: {str(e)}"

class HTTPParams(BaseModel):
    url: str = Field(..., description="Target URL")
    method: str = Field("GET", description="HTTP Method", pattern="^(GET|POST|PUT|DELETE|PATCH)$")
    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP Headers")

class HTTPNode(NodeImplementation[HTTPParams]):
    params_model = HTTPParams

    def execute(self, inputs: Dict[str, Any], context: Context, node_def: NodeDef[HTTPParams]) -> Any:
        params = node_def.params
        url = params.url
        method = params.method
        # Mock HTTP call
        return {"status": 200, "body": f"Response from {method} {url}"}

class ToolParams(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to execute")

class ToolNode(NodeImplementation[ToolParams]):
    params_model = ToolParams

    def execute(self, inputs: Dict[str, Any], context: Context, node_def: NodeDef[ToolParams]) -> Any:
        params = node_def.params
        tool_name = params.tool_name
        tool_args = inputs.get("tool_args", {})
        # Mock Tool call
        return f"Tool {tool_name} executed with {tool_args}"

class ConditionParams(BaseModel):
    expression: str = Field("True", description="Python expression to evaluate")
    true_target: Optional[str] = Field(None, description="Node ID to go to if true")
    false_target: Optional[str] = Field(None, description="Node ID to go to if false")

class ConditionNode(NodeImplementation[ConditionParams]):
    params_model = ConditionParams

    def execute(self, inputs: Dict[str, Any], context: Context, node_def: NodeDef[ConditionParams]) -> Any:
        params = node_def.params
        expression = params.expression
        true_target = params.true_target
        false_target = params.false_target
        
        # Simple eval context
        # We allow accessing inputs via 'input' or directly by name
        eval_context = inputs.copy()
        eval_context["input"] = inputs # Alias for convenience
        
        try:
            # WARNING: eval is unsafe. In production use a safe evaluator like simpleeval
            # We use a limited scope
            result = eval(expression, {"__builtins__": {}}, eval_context)
        except Exception as e:
            print(f"Condition eval failed: {e}")
            result = False
            
        return true_target if result else false_target

class LoopParams(BaseModel):
    expression: str = Field("True", description="Loop condition expression")
    body_target: Optional[str] = Field(None, description="Node ID for loop body")
    end_target: Optional[str] = Field(None, description="Node ID to exit loop")

class LoopNode(NodeImplementation[LoopParams]):
    """
    LoopNode acts as a conditional router for loops.
    It evaluates an expression to decide whether to continue the loop (body_target)
    or exit (end_target).
    """
    params_model = LoopParams

    def execute(self, inputs: Dict[str, Any], context: Context, node_def: NodeDef[LoopParams]) -> Any:
        params = node_def.params
        expression = params.expression
        
        true_target = params.body_target
        false_target = params.end_target
        
        eval_context = inputs.copy()
        eval_context["input"] = inputs
        
        try:
            result = eval(expression, {"__builtins__": {}}, eval_context)
        except Exception as e:
            print(f"Loop eval failed: {e}")
            result = False
            
        return true_target if result else false_target
