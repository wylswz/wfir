The project is managed by uv, which has three subprojects

- wfir (uv subproject): core IR model, runtime and basic langgraph transpiler
- api (uv subproject): provide rest api service
- ui(npm managed): frontend used to build workflows (drag and drop)

wfir is the core of the project, while and the rest are just used for demonstrate the capability.

The design must be as simple as possible for non-core features.

To add dependencies,
```
uv add <name>
```

Always use uv to run scripts in a uv project, or you will die.