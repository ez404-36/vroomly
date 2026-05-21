import type { ReactNode } from 'react';
import { Text } from '../../ui';
import { Checkbox } from '../../ui';

interface RecommendationCardProps {
  title: string;
  description: ReactNode;
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
}

export const RecommendationCard = ({
  title,
  description,
  checked,
  onCheckedChange,
}: RecommendationCardProps) => {
  return (
    <div className="flex flex-col gap-3 p-4 bg-(--color-surface) border border-(--color-border) rounded-xl min-w-[280px] max-w-[320px] flex-shrink-0 snap-start">
      <div className="flex items-start justify-between gap-2">
        <Text fw="semibold" size="sm" className="flex-1">
          {title}
        </Text>
        <Checkbox
          checked={checked}
          onCheckedChange={onCheckedChange}
          className="flex-shrink-0"
        />
      </div>
      <div className="text-(--color-text-muted)">{description}</div>
    </div>
  );
};