import { DatePickerInput } from '../../ui';
import type { DatePickerInputProps } from '../../ui';

export const CustomDatePickerInput = (props: DatePickerInputProps) => {
  // UI DatePickerInput already has default props:
  // placeholder="Выберите дату", valueFormat="DD-MM-YYYY", popoverProps={{ position: 'top' }}
  return <DatePickerInput className="datepicker-fixed" {...props} />;
};