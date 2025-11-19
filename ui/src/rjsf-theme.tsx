import type { WidgetProps, RegistryWidgetsType } from '@rjsf/utils';
import React from 'react';
import { Input } from './components/ui/input';
import { Textarea } from './components/ui/textarea';
import { Label } from './components/ui/label';
import { Select } from './components/ui/select';

// Custom RJSF Widgets using our UI components

export const CustomTextWidget = ({ id, placeholder, required, readonly, disabled, value, onChange, onBlur, onFocus, autofocus, options }: WidgetProps) => {
  const _onChange = ({ target: { value } }: React.ChangeEvent<HTMLInputElement>) => onChange(value === '' ? options.emptyValue : value);
  const _onBlur = ({ target: { value } }: React.FocusEvent<HTMLInputElement>) => onBlur(id, value);
  const _onFocus = ({ target: { value } }: React.FocusEvent<HTMLInputElement>) => onFocus(id, value);

  return (
    <Input
      id={id}
      placeholder={placeholder}
      required={required}
      disabled={disabled || readonly}
      value={value || value === 0 ? value : ''}
      onChange={_onChange}
      onBlur={_onBlur}
      onFocus={_onFocus}
      autoFocus={autofocus}
      type={(options.inputType as string) || 'text'}
    />
  );
};

export const CustomTextareaWidget = ({ id, placeholder, required, readonly, disabled, value, onChange, autofocus, options }: WidgetProps) => {
  const _onChange = ({ target: { value } }: React.ChangeEvent<HTMLTextAreaElement>) => onChange(value === '' ? options.emptyValue : value);
  
  return (
    <Textarea
      id={id}
      placeholder={placeholder}
      required={required}
      disabled={disabled || readonly}
      value={value || ''}
      onChange={_onChange}
      autoFocus={autofocus}
      rows={options.rows || 3}
    />
  );
};

export const CustomCheckboxWidget = ({ id, value, disabled, readonly, label, onChange }: WidgetProps) => {
  return (
    <div className="flex items-center space-x-2">
      <input
        type="checkbox"
        id={id}
        checked={typeof value === 'undefined' ? false : value}
        disabled={disabled || readonly}
        onChange={(event) => onChange(event.target.checked)}
        className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
      />
      <Label htmlFor={id}>{label}</Label>
    </div>
  );
};

export const CustomSelectWidget = ({ id, options, value, required, disabled, readonly, onChange, multiple }: WidgetProps) => {
  const { enumOptions, enumDisabled } = options;
  
  return (
    <Select
      id={id}
      multiple={multiple}
      value={value}
      required={required}
      disabled={disabled || readonly}
      onChange={(event: React.ChangeEvent<HTMLSelectElement>) => onChange(event.target.value)}
    >
      {enumOptions?.map(({ value, label }, i) => (
        <option key={i} value={value} disabled={enumDisabled && (enumDisabled as any).indexOf(value) !== -1}>
          {label}
        </option>
      ))}
    </Select>
  );
};

export const customWidgets: RegistryWidgetsType = {
  TextWidget: CustomTextWidget,
  TextareaWidget: CustomTextareaWidget,
  CheckboxWidget: CustomCheckboxWidget,
  SelectWidget: CustomSelectWidget,
};
