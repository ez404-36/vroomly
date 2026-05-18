import { DatePickerInput, DatePickerInputProps } from '@mantine/dates';

export const CustomDatePickerInput = (props: DatePickerInputProps) => {
  return (
    <DatePickerInput
      placeholder="Выберите дату"
      valueFormat="DD-MM-YYYY"
      className="datepicker-fixed"
      popoverProps={{ position: 'top' }}
      {...props}
    />
  );
};
