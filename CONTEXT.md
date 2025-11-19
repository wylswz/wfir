# Project Status & TODOs

This file maintains the CONTEXT of the project, update it as you move on.

## Context
Workflow IR (WFIR) is a portable intermediate representation for AI workflows.
Current implementation includes:
- **IR Models**: Pydantic models in `wfir/src/wfir/models.py`.
- **Verifier**: Static analysis in `wfir/src/wfir/verifier.py`.
- **Compiler**: LangGraph transpiler in `wfir/src/wfir/compiler/langgraph/`.
- **Runtime**: Basic protocols and standard nodes in `wfir/src/wfir/runtime/`.
- **CLI**: Command-line interface for compilation.

## TODO List

- [x] Define IR Models (Nodes, Edges, Inputs, Context)
- [x] Implement Verifier (Cycles, Data Flow, Condition validation)
- [x] Implement LangGraph Transpiler (Visitor Pattern)
- [x] **CLI Integration**: Create a `uv`-compatible CLI command (e.g., `compile`).
  - use should be able to use like this `uv compile ir.json --target=langgraph > g.py`
- [x] **Runtime Library**: Implement actual execution logic for standard nodes.
- [x] **Node Library**: Add standard nodes (LLM, HTTP, Tool, Condition, Loop).
- [x] **Documentation**: Expand `DESIGN.md` with usage examples.
- [x] **Testing**: Add integration tests for the full compilation pipeline.

## Technical Decisions
- **Expression Language**: Using simple strings (CEL-like) for conditions.
- **Transpilation**: Visitor pattern with Jinja2 templates.
- **Graph Structure**: Explicit edges list; Condition nodes use `params` for targets but must match graph edges.
- **Runtime Interface**: Generated nodes pass raw node definition to runtime for context.
- **Compilation**: Generated code returns `StateGraph` object, allowing user to compile/extend it.
- **Condition/Loop**: Implemented as runtime nodes that evaluate expressions and return the next node ID for routing.
