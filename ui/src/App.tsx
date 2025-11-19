import { useState, useEffect, useCallback } from 'react';
import { 
  ReactFlow, 
  Controls, 
  Background, 
  useNodesState, 
  useEdgesState, 
  addEdge,
  type Connection,
  type Edge as FlowEdge,
  type Node as FlowNode,
  MarkerType,
  useReactFlow,
  ReactFlowProvider,
  type OnNodesChange,
  type OnEdgesChange,
  type OnConnect
} from '@xyflow/react';
import { getWorkflows, getWorkflow, updateWorkflow, runWorkflow, createWorkflow, transpileWorkflow, getNodeTypes } from './api';
import { Play, Save, Plus, FileJson, Code, Download } from 'lucide-react';
import { ContextMenu } from './ContextMenu';
import { NodeConfigDrawer } from './NodeConfigDrawer';

interface Workflow {
  id: string;
  name: string;
}

interface WFIRNode {
  id: string;
  type: string;
  inputs?: Record<string, unknown>;
  outputs?: Record<string, unknown>;
  params?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  [key: string]: unknown;
}

interface WFIREdge {
  source: string;
  target: string;
  condition?: string | null;
  [key: string]: unknown;
}

interface WFIRWorkflow {
  nodes: WFIRNode[];
  edges: WFIREdge[];
  [key: string]: unknown;
}

// Helper to convert WFIR to ReactFlow
const wfirToFlow = (wfir: WFIRWorkflow) => {
  const nodes: FlowNode[] = wfir.nodes.map((n, index) => ({
    id: n.id,
    type: 'default', // Using default for now, can be custom
    data: { 
      label: `${n.type} (${n.id})`,
      ...n // Store full node data in data object
    },
    position: (n.metadata?.position as { x: number; y: number }) || { x: 100 + index * 150, y: 100 + index * 50 }
  }));

  const edges: FlowEdge[] = wfir.edges.map((e, index) => ({
    id: `e-${index}`,
    source: e.source,
    target: e.target,
    label: e.condition,
    markerEnd: { type: MarkerType.ArrowClosed },
  }));

  return { nodes, edges };
};

// Helper to convert ReactFlow to WFIR (partial, updates structure)
const flowToWfir = (nodes: FlowNode[], edges: FlowEdge[], originalWfir: WFIRWorkflow) => {
  const newNodes = nodes.map(n => {
    // Try to find original node to preserve other fields if not in data
    const original = originalWfir.nodes.find((on) => on.id === n.id);
    
    // Data from ReactFlow node (updated via drawer)
    const nodeData = n.data as Record<string, unknown>;

    return {
      ...original,
      ...nodeData, // Overwrite with updated data
      id: n.id, // Ensure ID matches
      // If it's a new node, we need defaults.
      type: (nodeData.type as string) || original?.type || 'StartNode', 
      metadata: { ...(original?.metadata as object), position: n.position },
      // Remove label from data when saving back to WFIR if it was added for display
      label: undefined 
    } as WFIRNode;
  });

  const newEdges = edges.map(e => ({
    source: e.source,
    target: e.target,
    condition: e.label as string
  }));

  return {
    ...originalWfir,
    nodes: newNodes,
    edges: newEdges
  };
};

interface FlowEditorProps {
  nodes: FlowNode[];
  edges: FlowEdge[];
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
  setNodes: React.Dispatch<React.SetStateAction<FlowNode[]>>;
  menu: { id: string; top: number; left: number; right: number; bottom: number } | null;
  setMenu: (menu: { id: string; top: number; left: number; right: number; bottom: number } | null) => void;
  onNodeClick: (event: React.MouseEvent, node: FlowNode) => void;
}

function FlowEditor({ 
  nodes, 
  edges, 
  onNodesChange, 
  onEdgesChange, 
  onConnect, 
  setNodes,
  menu,
  setMenu,
  onNodeClick,
  availableNodeTypes
}: FlowEditorProps & { availableNodeTypes: string[] }) {
  const { screenToFlowPosition } = useReactFlow();

  const onPaneContextMenu = useCallback(
    (event: React.MouseEvent | MouseEvent) => {
      event.preventDefault();
      const e = event as React.MouseEvent;
      
      setMenu({
        id: 'pane-menu',
        top: e.clientY,
        left: e.clientX,
        right: 0,
        bottom: 0,
      });
    },
    [setMenu],
  );

  const onPaneClick = useCallback(() => {
    setMenu(null);
  }, [setMenu]);

  const handleAddNode = useCallback((type: string, position: { x: number; y: number }) => {
    const id = `${type.toLowerCase()}-${Date.now()}`;
    
    // Convert screen coordinates to flow coordinates
    const flowPosition = screenToFlowPosition({
      x: position.x,
      y: position.y,
    });

    const newNode: FlowNode = {
      id,
      type: 'default',
      position: flowPosition, 
      data: { 
        label: `${type} (${id})`,
        id,
        type,
        inputs: {},
        params: {},
        outputs: { output: "Any" }
      },
    };

    setNodes((nds) => nds.concat(newNode));
  }, [setNodes, screenToFlowPosition]);

  return (
    <>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onPaneContextMenu={onPaneContextMenu}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
      
      {menu && (
        <ContextMenu
          {...menu}
          onAddNode={handleAddNode}
          onClose={() => setMenu(null)}
          availableNodeTypes={availableNodeTypes}
        />
      )}
    </>
  );
}

function App() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [currentWfir, setCurrentWfir] = useState<WFIRWorkflow | null>(null);
  
  const [nodes, setNodes, onNodesChange] = useNodesState<FlowNode>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<FlowEdge>([]);
  
  const [output, setOutput] = useState<string>('');
  const [transpiledCode, setTranspiledCode] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<'editor' | 'json' | 'code'>('editor');

  // Context Menu State
  const [menu, setMenu] = useState<{ id: string; top: number; left: number; right: number; bottom: number } | null>(null);

  // Drawer State
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedNodeData, setSelectedNodeData] = useState<{ id: string; type: string; inputs?: any; params?: any; outputs?: any } | null>(null);
  const [nodeSchemas, setNodeSchemas] = useState<Record<string, object>>({});

  useEffect(() => {
    // Load node schemas initially
    getNodeTypes().then(schemas => setNodeSchemas(schemas)).catch(console.error);
  }, []);

  const loadWorkflows = useCallback(async () => {
    try {
      // Only load workflows here
      const workflowsData = await getWorkflows();
      setWorkflows(workflowsData);
      if (workflowsData.length > 0 && !selectedId) {
        setSelectedId(workflowsData[0].id);
      }
    } catch (error) {
      console.error('Failed to load workflows', error);
    }
  }, [selectedId]);

  useEffect(() => {
    loadWorkflows();
  }, [loadWorkflows]);

  const loadWorkflow = useCallback(async (id: string) => {
    try {
      const data = await getWorkflow(id);
      setCurrentWfir(data);
      const { nodes: flowNodes, edges: flowEdges } = wfirToFlow(data);
      setNodes(flowNodes);
      setEdges(flowEdges);
      setOutput('');
      setTranspiledCode('');
    } catch (error) {
      console.error('Failed to load workflow', error);
    }
  }, [setNodes, setEdges]);

  useEffect(() => {
    if (selectedId) {
      loadWorkflow(selectedId);
    } else {
      setCurrentWfir(null);
      setNodes([]);
      setEdges([]);
      setOutput('');
      setTranspiledCode('');
    }
  }, [selectedId, loadWorkflow, setNodes, setEdges]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  const onNodeClick = useCallback((_event: React.MouseEvent, node: FlowNode) => {
    setSelectedNodeData({
      id: node.id,
      type: (node.data.type as string) || 'default',
      inputs: node.data.inputs,
      params: node.data.params,
      outputs: node.data.outputs,
    });
    setDrawerOpen(true);
  }, []);

  const handleUpdateNode = (nodeId: string, data: Record<string, unknown>) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            id: data.id as string, 
            data: {
              ...node.data,
              ...data,
              label: `${data.type} (${data.id})`
            }
          };
        }
        return node;
      })
    );
  };

  const handleSave = async () => {
    if (!selectedId || !currentWfir) return;
    try {
      const updatedWfir = flowToWfir(nodes, edges, currentWfir);
      await updateWorkflow(selectedId, updatedWfir);
      setCurrentWfir(updatedWfir);
      alert('Saved!');
      loadWorkflows();
    } catch {
      alert('Save Failed');
    }
  };

  const handleRun = async () => {
    if (!selectedId || !currentWfir) return;
    setLoading(true);
    try {
      // Auto-save before run to ensure latest changes are used
      const updatedWfir = flowToWfir(nodes, edges, currentWfir);
      await updateWorkflow(selectedId, updatedWfir);
      setCurrentWfir(updatedWfir);
      
      const result = await runWorkflow(selectedId, {});
      setOutput(JSON.stringify(result, null, 2));
      setViewMode('json'); // Switch to see output
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } }, message?: string };
      setOutput(`Error: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleTranspile = async () => {
    if (!selectedId || !currentWfir) return;
    try {
      // Auto-save before transpilation to ensure latest changes are used
      const updatedWfir = flowToWfir(nodes, edges, currentWfir);
      await updateWorkflow(selectedId, updatedWfir);
      setCurrentWfir(updatedWfir);

      const result = await transpileWorkflow(selectedId);
      setTranspiledCode(result.code);
      setViewMode('code');
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } }, message?: string };
      alert(`Transpile Failed: ${err.response?.data?.detail || err.message}`);
    }
  };

  const handleCreate = async () => {
    const newWorkflow = {
      name: "New Workflow",
      nodes: [
        { id: "start", type: "StartNode", metadata: { position: { x: 100, y: 100 } } },
        { id: "end", type: "EndNode", metadata: { position: { x: 400, y: 100 } } }
      ],
      edges: [
        { source: "start", target: "end" }
      ]
    };
    try {
      const created = await createWorkflow(newWorkflow);
      await loadWorkflows();
      setSelectedId(created.id);
    } catch (error) {
      console.error("Failed to create", error);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200 flex justify-between items-center">
          <h1 className="font-bold text-lg">WFIR Workflows</h1>
          <button onClick={handleCreate} className="p-1 hover:bg-gray-100 rounded">
            <Plus size={20} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto">
          {workflows.map(w => (
            <div
              key={w.id}
              onClick={() => setSelectedId(w.id)}
              className={`p-3 cursor-pointer hover:bg-gray-50 flex items-center gap-2 ${selectedId === w.id ? 'bg-blue-50 border-r-2 border-blue-500' : ''}`}
            >
              <FileJson size={16} className="text-gray-500" />
              <span className="truncate">{w.name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col relative">
        {selectedId ? (
          <>
            <div className="p-4 bg-white border-b border-gray-200 flex gap-2 items-center">
              <div className="flex bg-gray-100 rounded p-1 mr-4">
                <button 
                  onClick={() => setViewMode('editor')}
                  className={`px-3 py-1 rounded text-sm ${viewMode === 'editor' ? 'bg-white shadow text-blue-600' : 'text-gray-600'}`}
                >
                  Editor
                </button>
                <button 
                  onClick={() => setViewMode('json')}
                  className={`px-3 py-1 rounded text-sm ${viewMode === 'json' ? 'bg-white shadow text-blue-600' : 'text-gray-600'}`}
                >
                  JSON / Output
                </button>
                <button 
                  onClick={() => setViewMode('code')}
                  className={`px-3 py-1 rounded text-sm ${viewMode === 'code' ? 'bg-white shadow text-blue-600' : 'text-gray-600'}`}
                >
                  Code
                </button>
              </div>

              <div className="flex-1"></div>

              <button
                onClick={handleSave}
                className="flex items-center gap-2 px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-700"
              >
                <Save size={16} /> Save
              </button>
              <button
                onClick={handleTranspile}
                className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-500"
              >
                <Code size={16} /> Transpile
              </button>
              <button
                onClick={handleRun}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-500 disabled:opacity-50"
              >
                <Play size={16} /> {loading ? 'Running...' : 'Run'}
              </button>
            </div>

            <div className="flex-1 relative">
              {viewMode === 'editor' && (
                <div className="absolute inset-0">
                  <ReactFlowProvider>
                    <FlowEditor 
                      nodes={nodes}
                      edges={edges}
                      onNodesChange={onNodesChange}
                      onEdgesChange={onEdgesChange}
                      onConnect={onConnect}
                      setNodes={setNodes}
                      menu={menu}
                      setMenu={setMenu}
                      onNodeClick={onNodeClick}
                      availableNodeTypes={Object.keys(nodeSchemas)}
                    />
                  </ReactFlowProvider>
                </div>
              )}

              {viewMode === 'json' && (
                <div className="absolute inset-0 flex">
                  <div className="flex-1 p-4 flex flex-col gap-2">
                    <label className="font-semibold text-gray-700">Workflow JSON</label>
                    <textarea
                      className="flex-1 w-full p-4 font-mono text-sm border border-gray-300 rounded resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={currentWfir ? JSON.stringify(currentWfir, null, 2) : ''}
                      readOnly
                    />
                  </div>
                  <div className="flex-1 p-4 flex flex-col gap-2 bg-gray-50 border-l border-gray-200">
                    <label className="font-semibold text-gray-700">Output</label>
                    <pre className="flex-1 w-full p-4 font-mono text-sm bg-white border border-gray-300 rounded overflow-auto">
                      {output}
                    </pre>
                  </div>
                </div>
              )}

              {viewMode === 'code' && (
                <div className="absolute inset-0 p-4 flex flex-col">
                  <div className="flex justify-between items-center mb-2">
                    <label className="font-semibold text-gray-700">LangGraph Code</label>
                    <button 
                      onClick={() => {
                        const blob = new Blob([transpiledCode], { type: 'text/python' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'workflow.py';
                        a.click();
                      }}
                      className="flex items-center gap-1 text-sm text-blue-600 hover:underline"
                    >
                      <Download size={14} /> Download
                    </button>
                  </div>
                  <textarea
                    className="flex-1 w-full p-4 font-mono text-sm border border-gray-300 rounded resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-900 text-gray-100"
                    value={transpiledCode}
                    readOnly
                    placeholder="Click 'Transpile' to generate code..."
                  />
                </div>
              )}
            </div>
            
            <NodeConfigDrawer
              node={selectedNodeData}
              isOpen={drawerOpen}
              onClose={() => setDrawerOpen(false)}
              onSave={handleUpdateNode}
              schemas={nodeSchemas}
            />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            Select a workflow to start
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
