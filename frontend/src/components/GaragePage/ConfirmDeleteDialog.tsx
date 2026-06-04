import type { ReactNode } from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { Button, Stack, Text } from '../../ui';

interface ConfirmDeleteDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Заголовок диалога (например, «Удалить автомобиль»). */
  title: string;
  /** Основной вопрос-подтверждение. */
  body: ReactNode;
  /** Дополнительное пояснение/предупреждение под основным текстом. */
  note?: ReactNode;
  /** Подпись кнопки подтверждения. */
  confirmLabel?: string;
  /** Подпись кнопки отмены. */
  cancelLabel?: string;
  onConfirm: () => void;
}

/**
 * Переиспользуемый диалог подтверждения удаления.
 *
 * Единая разметка для удаления ТС и напоминаний (раньше дублировалась двумя
 * инлайновыми `Dialog.Root` в GaragePage). Закрытие через крестик/Esc/оверлей
 * приходит через `onOpenChange(false)`; кнопка «Отмена» делает то же самое.
 */
export function ConfirmDeleteDialog({
  open,
  onOpenChange,
  title,
  body,
  note,
  confirmLabel = 'Удалить',
  cancelLabel = 'Отмена',
  onConfirm,
}: ConfirmDeleteDialogProps) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-40" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2 w-full max-w-md rounded-lg bg-(--color-surface) p-6 shadow-xl">
          <Dialog.Title className="text-lg font-semibold text-(--color-text) mb-4">
            {title}
          </Dialog.Title>
          <Stack gap="md">
            <Text>{body}</Text>
            {note && (
              <Text size="sm" c="dimmed">
                {note}
              </Text>
            )}
            <div className="flex justify-end gap-3">
              <Button variant="ghost" onClick={() => onOpenChange(false)}>
                {cancelLabel}
              </Button>
              <Button variant="danger" onClick={onConfirm}>
                {confirmLabel}
              </Button>
            </div>
          </Stack>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
