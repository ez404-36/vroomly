import type { UserVehicleDetailSchema } from '../../types/schema-types';
import { Text } from '../../ui';
import { Button } from '../../ui';

interface VehicleCardProps {
  vehicle: UserVehicleDetailSchema;
  onEdit: (vehicle: UserVehicleDetailSchema) => void;
  onDelete: (vehicle: UserVehicleDetailSchema) => void;
  large?: boolean;
}

export const VehicleCard = ({
  vehicle,
  onEdit,
  onDelete,
  large = false,
}: VehicleCardProps) => {
  const getVehicleDisplayName = (v: UserVehicleDetailSchema) => {
    const parts = [v.brand, v.series].filter(Boolean);
    return parts.length > 0 ? parts.join(' ') : 'Неизвестное ТС';
  };

  const getVehicleYear = (v: UserVehicleDetailSchema) => {
    return v.productionYear ? `(${v.productionYear})` : '';
  };

  return (
    <div
      className={`flex gap-4 p-5 bg-(--color-surface) border border-(--color-border) rounded-xl ${large ? 'min-w-[400px] max-w-[500px] flex-shrink-0 snap-start' : 'min-w-[300px] flex-shrink-0 snap-start'} transition-opacity duration-300 ease-in-out`}
    >
      <div
        className={`flex items-center justify-center rounded-xl text-(--color-primary) flex-shrink-0 ${large ? 'w-20 h-20 bg-(--color-primary-subtle)' : 'w-14 h-14 bg-(--color-primary-subtle)'}`}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width={large ? 40 : 28}
          height={large ? 40 : 28}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1-.8-1.8-.8H5c-.6 0-1 .4-1 1v4c0 .6.4 1 1 1h2" />
          <circle cx="7" cy="17" r="2" />
          <circle cx="17" cy="17" r="2" />
          <path d="M14 17H9" />
          <path d="M5 10h14" />
        </svg>
      </div>
      <div className="flex flex-col flex-1 gap-3">
        <div className="flex gap-3 items-center">
          <Text fw="semibold" size={large ? 'lg' : 'sm'}>
            {getVehicleDisplayName(vehicle)}
          </Text>
          <Text size={large ? 'md' : 'sm'} c="dimmed">
            {getVehicleYear(vehicle)}
          </Text>
        </div>
        <div className="flex flex-wrap gap-2">
          {vehicle.color && (
            <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-(--color-bg-muted) text-(--color-text-muted)">
              {vehicle.color}
            </span>
          )}
          {vehicle.generation && (
            <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-(--color-bg-muted) text-(--color-text-muted)">
              {vehicle.generation}
            </span>
          )}
          {vehicle.mileage != null && (
            <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-(--color-bg-muted) text-(--color-text-muted)">
              {vehicle.mileage.toLocaleString('ru-RU')} км
            </span>
          )}
        </div>
        <div className="flex gap-2 mt-1">
          <Button variant="ghost" size="xs" onClick={() => onEdit(vehicle)}>
            Редактировать
          </Button>
          <Button variant="danger" size="xs" onClick={() => onDelete(vehicle)}>
            Удалить
          </Button>
        </div>
      </div>
    </div>
  );
};
