import { useEffect, useState } from 'react';
import { combineDateAndTime } from '../../utils/garage';
import type {
  ReminderFormValue,
  ReminderModalInitialValue,
} from '../../components/GaragePage/AddReminderModal';

const EMPTY_INITIAL: ReminderModalInitialValue = {
  title: '',
  description: '',
  date: null,
  time: null,
  allDay: false,
};

export interface UseReminderFormResult {
  title: string;
  setTitle: (value: string) => void;
  description: string;
  setDescription: (value: string) => void;
  date: Date | null;
  setDate: (value: Date | null) => void;
  time: string | null;
  setTime: (value: string | null) => void;
  allDay: boolean;
  setAllDay: (value: boolean) => void;
  /** Готовое значение для отправки, либо `null` если title пустой. */
  buildValue: () => ReminderFormValue | null;
}

/**
 * Состояние формы напоминания: поля, синхронизация с `initialValue` при
 * открытии модалки и сборка итогового значения (через чистую `combineDateAndTime`).
 * Презентационная модалка остаётся без доменной логики дат.
 */
export function useReminderForm(
  open: boolean,
  initialValue: ReminderModalInitialValue | null | undefined,
): UseReminderFormResult {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [date, setDate] = useState<Date | null>(null);
  const [time, setTime] = useState<string | null>(null);
  const [allDay, setAllDay] = useState(false);

  useEffect(() => {
    // Синхронизируем поля формы с переданным напоминанием при открытии модалки.
    if (!open) {
      return;
    }
    const init = initialValue ?? EMPTY_INITIAL;
    /* eslint-disable react-hooks/set-state-in-effect */
    setTitle(init.title);
    setDescription(init.description);
    setDate(init.date);
    setTime(init.time);
    setAllDay(init.allDay);
    /* eslint-enable react-hooks/set-state-in-effect */
  }, [open, initialValue]);

  const buildValue = (): ReminderFormValue | null => {
    if (!title.trim()) {
      return null;
    }
    return {
      title: title.trim(),
      description: description.trim(),
      dateTime: combineDateAndTime(date, time, allDay),
      allDay,
    };
  };

  return {
    title,
    setTitle,
    description,
    setDescription,
    date,
    setDate,
    time,
    setTime,
    allDay,
    setAllDay,
    buildValue,
  };
}
