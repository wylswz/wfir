
interface ContextMenuProps {
  id: string;
  top: number;
  left: number;
  right: number;
  bottom: number;
  onAddNode: (type: string, position: { x: number; y: number }) => void;
  onClose: () => void;
}

const NODE_TYPES = [
  { type: 'StartNode', label: 'Start Node' },
  { type: 'EndNode', label: 'End Node' },
  { type: 'LLM', label: 'LLM' },
  { type: 'HTTP', label: 'HTTP Request' },
  { type: 'Tool', label: 'Tool' },
  { type: 'Condition', label: 'Condition' },
  { type: 'Loop', label: 'Loop' },
];

export const ContextMenu = ({ top, left, onAddNode, onClose }: ContextMenuProps) => {
  return (
    <div
      style={{ top, left }}
      className="fixed z-50 bg-white border border-gray-200 shadow-lg rounded-md py-1 min-w-[150px]"
    >
      <div className="px-3 py-2 text-xs font-semibold text-gray-500 border-b border-gray-100 mb-1">
        Add Node
      </div>
      {NODE_TYPES.map((node) => (
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

