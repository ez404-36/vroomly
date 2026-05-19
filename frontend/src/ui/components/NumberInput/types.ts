export interface NumberInputProps {
	label?: string;
	placeholder?: string;
	value?: number | string | undefined;
	onChange?: (value: number | undefined) => void;
	min?: number;
	max?: number;
	step?: number;
	decimalScale?: number;
	error?: string;
	disabled?: boolean;
	required?: boolean;
	className?: string;
}