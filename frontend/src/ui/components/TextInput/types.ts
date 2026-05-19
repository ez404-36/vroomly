export interface TextInputProps {
	label?: string;
	placeholder?: string;
	value?: string;
	onChange?: (value: string) => void;
	error?: string;
	disabled?: boolean;
	required?: boolean;
	mt?: string;
	className?: string;
	name?: string;
	type?: string;
}