import { PasswordInput as MantinePasswordInputBase } from '@mantine/core';
import type { PasswordInputProps } from './types';

export const MantinePasswordInput = (props: PasswordInputProps) => {
	const { label, placeholder, value, onChange, error, disabled, required, mt, ...rest } = props;

	return (
		<MantinePasswordInputBase
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