# WFIR
Workflow Intermediate Representation

This is a demo project to test LLM capability boundaries on programming. All coding are done by LLM, supervised by human.

# Notice
Google denied my request to switch region, so I couldn't access antigravity. So I used cursor + gemini 3 pro as an alternative.


```mermaid
flowchart TD
    subgraph Input
        IR["Workflow IR (JSON)"]
    end

    subgraph Compiler [WFIR Compiler]
        Loader["IR Loader/Validator"]
        Optimizer["Logical Optimizer"]
        Transpiler["LangGraph Transpiler"]
        Templates["Jinja2 Templates"]
        
        IR --> Loader
        Loader -->|WorkflowIR Object| Optimizer
        Optimizer -->|"Optimized IR (Parallelism, pruning, etc,...)"| Transpiler
        Templates -.-> Transpiler
    end

    subgraph Generated [Generated Artifacts]
        PyCode["Python Code"]
    end

    subgraph Runtime [WFIR Runtime]
        Registry["Node Registry"]
        Context["Runtime Context"]
        NodeImpl["Node Implementations"]
        
        Registry --> NodeImpl
    end

    subgraph LangGraph [LangGraph Ecosystem]
        StateGraph
        Runner["Compiled Graph"]
    end

    Transpiler -->|Generates| PyCode
    PyCode -->|Uses| Registry
    PyCode -->|Uses| Context
    PyCode -->|Builds| StateGraph
    StateGraph -->|Compiles to| Runner
    Runner -->|Executes| NodeImpl
```
