import { Select as MantineSelectBase } from '@mantine/core';
import type { SelectProps } from './types';

export const MantineSelect = (props: SelectProps) => {
	const { label, placeholder, value, onChange, options, error, disabled, searchable, clearable, required, ...rest } = props;

	const data = options.map((opt) => ({ value: opt.value, label: opt.label }));

	return (
		<MantineSelectBase
			label={label}
			placeholder={placeholder}
			value={value || null}
			onChange={onChange}
			data={data}
			error={error}
			disabled={disabled}
			searchable={searchable}
			clearable={clearable}
			required={required}
			{...rest}
		/>
	);
};