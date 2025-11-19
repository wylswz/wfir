import { useState, useEffect } from 'react';
import { X, Save } from 'lucide-react';
import Form from '@rjsf/core';
import validator from '@rjsf/validator-ajv8';
import type { RJSFSchema, UiSchema } from '@rjsf/utils';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Textarea } from './components/ui/textarea';
import { customWidgets } from './rjsf-theme';

interface NodeConfigDrawerProps {
  node: { id: string; type: string; inputs?: any; params?: any; outputs?: any } | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (nodeId: string, data: any) => void;
  schemas: Record<string, any>;
}

// Use our nice Textarea for the CodeWidget too
const CodeWidget = (props: any) => {
  return (
    <Textarea
      className="font-mono text-sm min-h-[100px]"
      value={props.value}
      required={props.required}
      onChange={(event) => props.onChange(event.target.value)}
    />
  );
};

const widgets = {
  ...customWidgets,
  CodeWidget: CodeWidget
};

// Custom Field Template to clean up the form layout
const CustomFieldTemplate = (props: any) => {
  const { id, classNames, label, help, required, description, errors, children } = props;
  return (
    <div className={classNames + " mb-4"}>
      {label && (
        <Label htmlFor={id} className="mb-2 block">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </Label>
      )}
      {description && <p className="text-sm text-gray-500 mb-1">{description}</p>}
      {children}
      {errors}
      {help}
    </div>
  );
};

const CustomObjectFieldTemplate = (props: any) => {
  return (
    <div className="space-y-2">
      {props.properties.map((element: any) => (
        <div key={element.name}>{element.content}</div>
      ))}
    </div>
  );
};

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
  }, [node]); // node is the dependency, so we update form when node changes

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
    } catch {
      alert('Invalid JSON in one of the fields');
    }
  };

  if (!isOpen) return null;

  const schema = (schemas[formData.type] || {}) as RJSFSchema;
  
  const uiSchema: UiSchema = {};
  if (schema.properties) {
    if (schema.properties['expression']) {
        uiSchema['expression'] = { "ui:widget": "CodeWidget" };
    }
    if (schema.properties['system_prompt']) {
        uiSchema['system_prompt'] = { "ui:widget": "textarea" };
    }
  }

  const hasParams = schema && schema.properties && Object.keys(schema.properties).length > 0;

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-white shadow-2xl transform transition-transform duration-300 ease-in-out z-50 flex flex-col border-l border-gray-200">
      <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
        <h2 className="font-semibold text-lg text-gray-900">Configure Node</h2>
        <Button variant="ghost" size="icon" onClick={onClose} className="hover:bg-gray-200">
          <X className="h-5 w-5" />
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-white">
        <div className="space-y-2">
          <Label htmlFor="node-id">Node ID</Label>
          <Input
            id="node-id"
            value={formData.id}
            onChange={(e) => setFormData({ ...formData, id: e.target.value })}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="node-type">Type</Label>
          <Input
            id="node-type"
            value={formData.type}
            disabled
            className="bg-gray-100 text-gray-500"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="node-inputs">Inputs (JSON)</Label>
          <CodeWidget 
            value={formData.inputs} 
            onChange={(val: string) => setFormData({ ...formData, inputs: val })} 
          />
          <p className="text-xs text-gray-500">Define static values or references.</p>
        </div>

        <div className="space-y-2">
          <Label>Params</Label>
          <div className="rounded-lg border border-gray-200 bg-gray-50/50 p-4">
            {hasParams ? (
              <Form
                schema={schema}
                uiSchema={uiSchema}
                widgets={widgets}
                validator={validator}
                formData={formData.params}
                onChange={(e) => setFormData({ ...formData, params: e.formData })}
                templates={{
                  FieldTemplate: CustomFieldTemplate,
                  ObjectFieldTemplate: CustomObjectFieldTemplate
                }}
                children={<></>} // Hide submit button
              />
            ) : (
               <div className="text-sm text-gray-500 italic text-center py-4">
                 No parameters available.
               </div>
            )}
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="node-outputs">Outputs (JSON)</Label>
          <CodeWidget 
            value={formData.outputs} 
            onChange={(val: string) => setFormData({ ...formData, outputs: val })} 
          />
        </div>
      </div>

      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <Button onClick={handleSave} className="w-full bg-blue-600 hover:bg-blue-700 text-white">
          <Save className="mr-2 h-4 w-4" /> Save Changes
        </Button>
      </div>
    </div>
  );
};
