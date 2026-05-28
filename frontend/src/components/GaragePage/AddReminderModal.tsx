import { useEffect, useState } from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import {
  TextInput,
  DatePickerInput,
  TimeInput,
  Checkbox,
  Button,
  Stack,
} from '../../ui';

export interface ReminderFormValue {
  title: string;
  description: string;
  dateTime: Date | null;
  allDay: boolean;
}

export interface ReminderModalInitialValue {
  title: string;
  description: string;
  date: Date | null;
  time: string | null;
  allDay: boolean;
}

interface AddReminderModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (reminder: ReminderFormValue) => void;
  mode?: 'create' | 'edit';
  initialValue?: ReminderModalInitialValue | null;
}

const EMPTY_INITIAL: ReminderModalInitialValue = {
  title: '',
  description: '',
  date: null,
  time: null,
  allDay: false,
};

export function AddReminderModal({
  open,
  onOpenChange,
  onSubmit,
  mode = 'create',
  initialValue,
}: AddReminderModalProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [date, setDate] = useState<Date | null>(null);
  const [time, setTime] = useState<string | null>(null);
  const [allDay, setAllDay] = useState(false);

  useEffect(() => {
    // Синхронизируем поля формы с переданным напоминанием при открытии модалки.
    if (open) {
      const init = initialValue ?? EMPTY_INITIAL;
      /* eslint-disable react-hooks/set-state-in-effect */
      setTitle(init.title);
      setDescription(init.description);
      setDate(init.date);
      setTime(init.time);
      setAllDay(init.allDay);
      /* eslint-enable react-hooks/set-state-in-effect */
    }
  }, [open, initialValue]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      return;
    }

    let dateTime: Date | null = null;
    if (date) {
      dateTime = new Date(date);
      if (!allDay && time) {
        const [hours, minutes] = time.split(':');
        dateTime.setHours(parseInt(hours, 10), parseInt(minutes, 10), 0, 0);
      } else {
        dateTime.setHours(0, 0, 0, 0);
      }
    }

    onSubmit({
      title: title.trim(),
      description: description.trim(),
      dateTime,
      allDay,
    });
    onOpenChange(false);
  };

  const handleCancel = () => {
    onOpenChange(false);
  };

  const isEdit = mode === 'edit';

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-40" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2 w-full max-w-md rounded-lg bg-(--color-surface) p-6 shadow-xl">
          <Dialog.Title className="text-lg font-semibold text-(--color-text) mb-4">
            {isEdit ? 'Редактировать напоминание' : 'Новое напоминание'}
          </Dialog.Title>
          <form onSubmit={handleSubmit}>
            <Stack gap="md">
              <TextInput
                label="Суть"
                placeholder="Введите название"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
              <TextInput
                label="Детали"
                placeholder="Дополнительная информация"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
              <div>
                <DatePickerInput label="Дата" value={date} onChange={setDate} />
                {date && (
                  <div className="mt-3">
                    <Checkbox
                      label="Весь день"
                      checked={allDay}
                      onCheckedChange={setAllDay}
                      className="mb-2"
                    />
                    {!allDay && (
                      <TimeInput
                        label="Время"
                        value={time}
                        onChange={setTime}
                      />
                    )}
                  </div>
                )}
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <Button type="button" variant="ghost" onClick={handleCancel}>
                  Отмена
                </Button>
                <Button type="submit" disabled={!title.trim()}>
                  {isEdit ? 'Сохранить' : 'Добавить'}
                </Button>
              </div>
            </Stack>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
