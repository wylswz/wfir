import pytest
from wfir.models import WorkflowIR, Node, Edge, InputValue, ValueFrom
from wfir.runner import WorkflowRunner

@pytest.mark.asyncio
async def test_linear_execution():
    node1 = Node(id="n1", type="Echo", inputs={"val": InputValue(value=1)})
    node2 = Node(id="n2", type="AddOne", inputs={"val": InputValue(valueFrom=ValueFrom(nodeId="n1", outputKey="output"))})
    
    wf = WorkflowIR(
        name="Test",
        nodes=[node1, node2],
        edges=[Edge(source="n1", target="n2")]
    )
    
    runner = WorkflowRunner(wf)

    async def echo_handler(i, c, n):
        return {"output": i["val"]}
    
    async def add_one_handler(i, c, n):
        return {"output": i["val"] + 1}

    runner.register_handler("Echo", echo_handler)
    runner.register_handler("AddOne", add_one_handler)
    
    results = await runner.run()
    assert results["n2"]["output"] == 2

@pytest.mark.asyncio
async def test_missing_dependency():
    # n2 depends on n1, but n1 is not in the list (or executed after n2 in this simple runner)
    # In our simple runner, order matters. If we put n2 first, it should fail.
    
    node1 = Node(id="n1", type="Echo", inputs={"val": InputValue(value=1)})
    node2 = Node(id="n2", type="AddOne", inputs={"val": InputValue(valueFrom=ValueFrom(nodeId="n1", outputKey="output"))})
    
    wf = WorkflowIR(
        name="Test Fail",
        nodes=[node2, node1], # Wrong order for simple runner
        edges=[Edge(source="n1", target="n2")]
    )
    
    runner = WorkflowRunner(wf)
    
    async def echo_handler(i, c, n):
        return {"output": i["val"]}
    
    async def add_one_handler(i, c, n):
        return {"output": i["val"] + 1}

    runner.register_handler("Echo", echo_handler)
    runner.register_handler("AddOne", add_one_handler)
    
    with pytest.raises(RuntimeError, match="depends on 'n1' which has not executed yet"):
        await runner.run()
