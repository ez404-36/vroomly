import { useState } from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { TextInput, DatePickerInput, TimeInput, Checkbox, Button, Stack } from '../../ui';

interface AddReminderModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onAdd: (reminder: { title: string; description: string; dateTime: Date | null; allDay: boolean }) => void;
}

export function AddReminderModal({ open, onOpenChange, onAdd }: AddReminderModalProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [date, setDate] = useState<Date | null>(null);
  const [time, setTime] = useState<string | null>(null);
  const [allDay, setAllDay] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    let dateTime: Date | null = null;
    if (date) {
      dateTime = new Date(date);
      if (!allDay && time) {
        const [hours, minutes] = time.split(':');
        dateTime.setHours(parseInt(hours, 10), parseInt(minutes, 10));
      } else {
        dateTime.setHours(0, 0, 0, 0);
      }
    }

    onAdd({ title: title.trim(), description: description.trim(), dateTime, allDay });
    handleClose();
  };

  const handleClose = () => {
    setTitle('');
    setDescription('');
    setDate(null);
    setTime(null);
    setAllDay(false);
    onOpenChange(false);
  };

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-40" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2 w-full max-w-md rounded-lg bg-(--color-surface) p-6 shadow-xl">
          <Dialog.Title className="text-lg font-semibold text-(--color-text) mb-4">
            Новое напоминание
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
                <DatePickerInput
                  label="Дата"
                  value={date}
                  onChange={setDate}
                />
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
                <Button type="button" variant="ghost" onClick={handleClose}>
                  Отмена
                </Button>
                <Button type="submit" disabled={!title.trim()}>
                  Добавить
                </Button>
              </div>
            </Stack>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
