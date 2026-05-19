import { Switch as MantineSwitchBase } from '@mantine/core';
import type { SwitchProps } from './types';

export const MantineSwitch = (props: SwitchProps) => {
	const { label, checked, onChange, disabled, ...rest } = props;

	return (
		<MantineSwitchBase
			label={label}
			checked={checked}
			onChange={(e) => onChange?.(e.currentTarget.checked)}
			disabled={disabled}
			{...rest}
		/>
	);
};