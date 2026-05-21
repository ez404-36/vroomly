import type { UserVehicleDetailSchema } from '../../types/schema-types';
import { Text } from '../../ui';
import { Checkbox } from '../../ui';
import { ActionIcon } from '../../ui';

interface ReminderItemProps {
  id: string;
  text: string;
  date: string;
  checked: boolean;
  onCheckedChange: (id: string, checked: boolean) => void;
  onDelete: (id: string) => void;
}

export const ReminderItem = ({
  id,
  text,
  date,
  checked,
  onCheckedChange,
  onDelete,
}: ReminderItemProps) => {
  return (
    <div className="flex items-center gap-3 py-3 border-b border-(--color-border) last:border-b-0">
      <Checkbox
        checked={checked}
        onCheckedChange={(isChecked) => onCheckedChange(id, isChecked)}
        className="flex-shrink-0"
      />
      <Text
        size="sm"
        className={`flex-1 ${checked ? 'line-through text-(--color-text-muted)' : ''}`}
      >
        {text}
      </Text>
      <Text size="xs" c="dimmed" className="flex-shrink-0">
        {date}
      </Text>
      <ActionIcon
        variant="ghost"
        size="xs"
        onClick={() => onDelete(id)}
        className="flex-shrink-0 opacity-50 hover:opacity-100"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </ActionIcon>
    </div>
  );
};