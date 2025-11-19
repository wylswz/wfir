
interface ContextMenuProps {
  id: string;
  top: number;
  left: number;
  right: number;
  bottom: number;
  onAddNode: (type: string, position: { x: number; y: number }) => void;
  onClose: () => void;
  availableNodeTypes?: string[];
}

// const DEFAULT_NODE_TYPES = [
//   { type: 'StartNode', label: 'Start Node' },
//   { type: 'EndNode', label: 'End Node' },
//   { type: 'LLMNode', label: 'LLM' },
//   { type: 'HTTPNode', label: 'HTTP Request' },
//   { type: 'ToolNode', label: 'Tool' },
//   { type: 'ConditionNode', label: 'Condition' },
//   { type: 'LoopNode', label: 'Loop' },
// ];

export const ContextMenu = ({ top, left, onAddNode, onClose, availableNodeTypes }: ContextMenuProps) => {
  
  // If we have types from backend, use them.
  // We might want to map backend types to friendly labels if possible, 
  // or just use the type name.
  const nodeTypes = availableNodeTypes && availableNodeTypes.length > 0
    ? availableNodeTypes.map(t => ({ type: t, label: t }))
    : [];

  return (
    <div
      style={{ top, left }}
      className="fixed z-50 bg-white border border-gray-200 shadow-lg rounded-md py-1 min-w-[150px]"
    >
      <div className="px-3 py-2 text-xs font-semibold text-gray-500 border-b border-gray-100 mb-1">
        Add Node
      </div>
      {nodeTypes.map((node) => (
        <button
          key={node.type}
          className="w-full text-left px-3 py-2 text-sm hover:bg-blue-50 hover:text-blue-600 transition-colors"
          onClick={() => {
            onAddNode(node.type, { x: left, y: top });
            onClose();
          }}
        >
          {node.label}
        </button>
      ))}
    </div>
  );
};
