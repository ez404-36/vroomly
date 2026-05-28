import type {
  UserVehicleDetailSchema,
  UserVehicleListSchema,
} from '../../types/schema-types';
import { Text } from '../../ui';
import { Button } from '../../ui';

interface VehicleCardProps {
  vehicle: UserVehicleListSchema;
  detail?: UserVehicleDetailSchema | null;
  isDetailLoading?: boolean;
  onEdit: (vehicle: UserVehicleListSchema) => void;
  onDelete: (vehicle: UserVehicleListSchema) => void;
  onUpdateMileage?: (vehicle: UserVehicleListSchema) => void;
  large?: boolean;
}

interface Characteristic {
  label: string;
  value: string;
}

export const VehicleCard = ({
  vehicle,
  detail,
  isDetailLoading = false,
  onEdit,
  onDelete,
  onUpdateMileage,
  large = false,
}: VehicleCardProps) => {
  const getVehicleDisplayName = () => {
    const parts = [vehicle.brand, vehicle.series, vehicle.generation].filter(
      Boolean,
    );
    return parts.length > 0 ? parts.join(' ') : 'Неизвестное ТС';
  };

  const productionYear = detail?.productionYear ?? null;
  const year = productionYear ? `(${productionYear})` : '';

  const characteristics: Characteristic[] = [
    detail?.trim ? { label: 'Комплектация', value: detail.trim } : null,
    detail?.color ? { label: 'Цвет', value: detail.color } : null,
    detail?.avgFuelConsumption != null
      ? {
          label: 'Средний расход',
          value: `${detail.avgFuelConsumption.toLocaleString('ru-RU')} л/100км`,
        }
      : null,
    vehicle.mileage != null
      ? {
          label: 'Текущий пробег',
          value: `${vehicle.mileage.toLocaleString('ru-RU')} ${vehicle.isMileageInMiles ? 'миль' : 'км'}`,
        }
      : null,
  ].filter((item): item is Characteristic => item !== null);

  return (
    <div
      className={`flex gap-4 p-5 bg-(--color-surface) border border-(--color-border) rounded-xl ${large ? 'w-full min-w-[400px] snap-start' : 'min-w-[300px] flex-shrink-0 snap-start'} transition-opacity duration-300 ease-in-out`}
    >
      <div
        className={`flex items-center justify-center self-stretch aspect-square rounded-xl text-(--color-primary) flex-shrink-0 bg-(--color-primary-subtle) ${large ? 'min-w-20' : 'min-w-14'}`}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="60%"
          height="60%"
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
            {getVehicleDisplayName()}
          </Text>
          <Text size={large ? 'md' : 'sm'} c="dimmed">
            {year}
          </Text>
        </div>
        {isDetailLoading ? (
          <div className="flex flex-col gap-1">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-4 rounded bg-(--color-bg-muted) animate-pulse"
              />
            ))}
          </div>
        ) : (
          characteristics.length > 0 && (
            <ul className="flex flex-col gap-1">
              {characteristics.map((item) => (
                <li
                  key={item.label}
                  className="flex justify-between items-baseline gap-3 text-xs"
                >
                  <Text size="sm" c="dimmed" className="flex-shrink-0">
                    {item.label}
                  </Text>
                  <Text size="sm" fw="medium" ta="right" className="min-w-0">
                    {item.value}
                  </Text>
                </li>
              ))}
            </ul>
          )
        )}
        <div className="flex flex-wrap gap-2 mt-1">
          {onUpdateMileage && (
            <Button
              variant="filled"
              size="xs"
              onClick={() => onUpdateMileage(vehicle)}
            >
              Обновить пробег
            </Button>
          )}
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
