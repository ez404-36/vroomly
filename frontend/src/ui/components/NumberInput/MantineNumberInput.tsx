import { NumberInput as MantineNumberInputBase } from '@mantine/core';
import type { NumberInputProps } from './types';

export const MantineNumberInput = (props: NumberInputProps) => {
	const { label, placeholder, value, onChange, min, max, step, decimalScale, error, disabled, required, ...rest } = props;

	return (
		<MantineNumberInputBase
			label={label}
			placeholder={placeholder}
			value={value}
			onChange={(val) => onChange?.(typeof val === 'number' ? val : undefined)}
			min={min}
			max={max}
			step={step}
			decimalScale={decimalScale}
			error={error}
			disabled={disabled}
			required={required}
			{...rest}
		/>
	);
};