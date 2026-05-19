import { TextInput as MantineTextInputBase } from '@mantine/core';
import type { TextInputProps } from './types';

export const MantineTextInput = (props: TextInputProps) => {
	const { label, placeholder, value, onChange, error, disabled, required, mt, ...rest } = props;

	return (
		<MantineTextInputBase
			label={label}
			placeholder={placeholder}
			value={value}
			onChange={(e) => onChange?.(e.currentTarget.value)}
			error={error}
			disabled={disabled}
			required={required}
			mt={mt}
			{...rest}
		/>
	);
};