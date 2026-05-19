export interface SwitchProps {
	label?: string;
	checked?: boolean;
	onChange?: (checked: boolean) => void;
	disabled?: boolean;
	className?: string;
	'data-testid'?: string;
}