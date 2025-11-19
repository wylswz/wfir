import { useState, useEffect } from 'react';
import { X, Save } from 'lucide-react';
import Form from '@rjsf/core';
import validator from '@rjsf/validator-ajv8';

interface NodeConfigDrawerProps {
  node: any;
  isOpen: boolean;
  onClose: () => void;
  onSave: (nodeId: string, data: any) => void;
  schemas: Record<string, any>;
}

export const NodeConfigDrawer = ({ node, isOpen, onClose, onSave, schemas }: NodeConfigDrawerProps) => {
  const [formData, setFormData] = useState<any>({
    id: '',
    type: '',
    inputs: '{}',
    params: {},
    outputs: '{}'
  });

  useEffect(() => {
    if (node) {
      setFormData({
        id: node.id,
        type: node.type,
        inputs: JSON.stringify(node.inputs || {}, null, 2),
        params: node.params || {},
        outputs: JSON.stringify(node.outputs || {}, null, 2)
      });
    }
  }, [node]);

  const handleSave = () => {
    try {
      const updatedNode = {
        ...node,
        id: formData.id,
        inputs: JSON.parse(formData.inputs),
        params: formData.params,
        outputs: JSON.parse(formData.outputs)
      };
      onSave(node.id, updatedNode);
      onClose();
    } catch (e) {
      alert('Invalid JSON in one of the fields');
    }
  };

  if (!isOpen) return null;

  const schema = schemas[formData.type] || {};
  const hasParams = schema && schema.properties && Object.keys(schema.properties).length > 0;

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-white shadow-xl transform transition-transform duration-300 ease-in-out z-50 flex flex-col border-l border-gray-200">
      <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
        <h2 className="font-bold text-lg text-gray-800">Configure Node</h2>
        <button onClick={onClose} className="p-1 hover:bg-gray-200 rounded text-gray-500">
          <X size={20} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Node ID</label>
          <input
            type="text"
            value={formData.id}
            onChange={(e) => setFormData({ ...formData, id: e.target.value })}
            className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
          <input
            type="text"
            value={formData.type}
            disabled
            className="w-full p-2 border border-gray-300 rounded bg-gray-100 text-gray-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Inputs (JSON)</label>
          <textarea
            value={formData.inputs}
            onChange={(e) => setFormData({ ...formData, inputs: e.target.value })}
            className="w-full p-2 border border-gray-300 rounded h-32 font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          />
          <p className="text-xs text-gray-500 mt-1">Define static values or references.</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Params</label>
          {hasParams ? (
            <div className="rjsf-wrapper">
               <Form
                schema={schema}
                validator={validator}
                formData={formData.params}
                onChange={(e) => setFormData({ ...formData, params: e.formData })}
                children={<></>} // Hide submit button
              />
            </div>
          ) : (
             <div className="text-sm text-gray-500 italic p-2 bg-gray-50 rounded border border-gray-200">
               No parameters available for this node type.
             </div>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Outputs (JSON)</label>
          <textarea
            value={formData.outputs}
            onChange={(e) => setFormData({ ...formData, outputs: e.target.value })}
            className="w-full p-2 border border-gray-300 rounded h-32 font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          />
        </div>
      </div>

      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <button
          onClick={handleSave}
          className="w-full flex justify-center items-center gap-2 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors"
        >
          <Save size={18} /> Save Changes
        </button>
      </div>
    </div>
  );
};
