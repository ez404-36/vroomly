import { useEffect, useState } from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { NumberInput, Switch, Button, Stack, Text } from '../../ui';

interface UpdateMileageModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initialMileage: number | null;
  initialIsMileageInMiles: boolean;
  isSubmitting?: boolean;
  error?: string | null;
  onSubmit: (data: { mileage: number; isMileageInMiles: boolean }) => void;
}

export function UpdateMileageModal({
  open,
  onOpenChange,
  initialMileage,
  initialIsMileageInMiles,
  isSubmitting = false,
  error,
  onSubmit,
}: UpdateMileageModalProps) {
  const [mileage, setMileage] = useState<number | undefined>(
    initialMileage ?? undefined,
  );
  const [isMileageInMiles, setIsMileageInMiles] = useState(
    initialIsMileageInMiles,
  );

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    if (open) {
      setMileage(initialMileage ?? undefined);
      setIsMileageInMiles(initialIsMileageInMiles);
    }
  }, [open, initialMileage, initialIsMileageInMiles]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const isValid = mileage !== undefined && mileage >= 0;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid || mileage === undefined) {
      return;
    }
    onSubmit({ mileage, isMileageInMiles });
  };

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-40" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2 w-full max-w-md rounded-lg bg-(--color-surface) p-6 shadow-xl">
          <Dialog.Title className="text-lg font-semibold text-(--color-text) mb-4">
            Обновить пробег
          </Dialog.Title>
          <form onSubmit={handleSubmit}>
            <Stack gap="md">
              <NumberInput
                label="Пробег"
                placeholder="Введите текущий пробег"
                value={mileage ?? ''}
                min={0}
                onValueChange={setMileage}
                required
              />
              <Switch
                label="Пробег в милях"
                checked={isMileageInMiles}
                onCheckedChange={setIsMileageInMiles}
              />
              {error && (
                <Text size="sm" c="red">
                  {error}
                </Text>
              )}
              <div className="flex justify-end gap-3 pt-2">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => onOpenChange(false)}
                >
                  Отмена
                </Button>
                <Button type="submit" disabled={!isValid || isSubmitting}>
                  Сохранить
                </Button>
              </div>
            </Stack>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
