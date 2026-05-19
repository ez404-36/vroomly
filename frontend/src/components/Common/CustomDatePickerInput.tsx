import { DatePickerInput } from '../../ui';
import type { DatePickerInputProps } from '../../ui';

export const CustomDatePickerInput = (props: DatePickerInputProps) => {
  return <DatePickerInput className="datepicker-fixed" {...props} />;
};
