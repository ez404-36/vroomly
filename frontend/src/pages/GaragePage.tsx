import { useState } from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import {
  Title,
  Text,
  Stack,
  Button,
} from '../ui';
import { Link, useNavigate } from 'react-router-dom';
import { routes } from '../utils/routes';
import {
  useGetUserVehiclesQuery,
  useDeleteUserVehicleMutation,
  type UserVehicleDetailSchema,
} from '../api/vehiclesApi';
import classes from '../styles/pages/Garage.module.css';

const GaragePage = () => {
  const navigate = useNavigate();
  const { data: vehicles, isLoading, error } = useGetUserVehiclesQuery();
  const [deleteVehicle] = useDeleteUserVehicleMutation();
  const [deleteModalOpened, setDeleteModalOpened] = useState(false);
  const [vehicleToDelete, setVehicleToDelete] =
    useState<UserVehicleDetailSchema | null>(null);

  const handleDeleteClick = (vehicle: UserVehicleDetailSchema) => {
    setVehicleToDelete(vehicle);
    setDeleteModalOpened(true);
  };

  const closeDeleteModal = () => {
    setDeleteModalOpened(false);
  };

  const handleConfirmDelete = async () => {
    if (vehicleToDelete) {
      try {
        await deleteVehicle(vehicleToDelete.id).unwrap();
        closeDeleteModal();
        setVehicleToDelete(null);
      } catch {
        closeDeleteModal();
      }
    }
  };

  const getVehicleDisplayName = (vehicle: UserVehicleDetailSchema) => {
    const parts = [vehicle.brand, vehicle.series].filter(Boolean);
    return parts.length > 0 ? parts.join(' ') : 'Неизвестное ТС';
  };

  const getVehicleYear = (vehicle: UserVehicleDetailSchema) => {
    return vehicle.production_year ? `(${vehicle.production_year})` : '';
  };

  return (
    <div className={classes.container}>
      <div className={classes.header}>
        <div className="flex justify-between items-start">
          <Stack gap={4}>
            <Title order={2} className={classes.title}>
              Мой гараж
            </Title>
            <Text size="sm" c="dimmed" className={classes.subtitle}>
              {vehicles && vehicles.length > 0
                ? `${vehicles.length} ${getVehicleCountWord(vehicles.length)}`
                : 'Добавьте свой первый автомобиль'}
            </Text>
          </Stack>
          <Link to={routes.addVehicle}>
            <Button className={classes.addButton}>
              + Добавить ТС
            </Button>
          </Link>
        </div>
      </div>

      {isLoading && (
        <Stack gap="md">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-24 rounded-md bg-[--color-bg-muted] animate-pulse"
            />
          ))}
        </Stack>
      )}

      {error && (
        <div className="rounded-md border border-[--color-danger] bg-[--color-danger]/10 px-4 py-3 text-sm text-[--color-danger]">
          Не удалось загрузить список автомобилей
        </div>
      )}

      {!isLoading && !error && vehicles && vehicles.length === 0 && (
        <div className={classes.emptyCard}>
          <Stack align="center" gap="md">
            <div className={classes.emptyIcon}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="48"
                height="48"
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
            <Stack gap={4} align="center">
              <Text fw="semibold" size="lg">
                В гараже пока пусто
              </Text>
              <Text size="sm" c="dimmed" ta="center">
                Добавьте свой первый автомобиль, чтобы отслеживать его
                обслуживание и расходы
              </Text>
            </Stack>
            <Link to={routes.addVehicle}>
              <Button size="md" className={classes.addButton}>
                + Добавить автомобиль
              </Button>
            </Link>
          </Stack>
        </div>
      )}

      {!isLoading && !error && vehicles && vehicles.length > 0 && (
        <Stack gap="md" className={classes.vehiclesList}>
          {vehicles.map((vehicle) => (
            <div key={vehicle.id} className={classes.vehicleCard} style={{ padding: '16px' }}>
              <div className="flex justify-between items-center flex-nowrap">
                <div className="flex gap-3 items-center flex-nowrap" style={{ flex: 1 }}>
                  <div className={classes.vehicleIcon}>
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="32"
                      height="32"
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
                  <Stack gap={4} style={{ flex: 1 }}>
                    <div className="flex gap-2 items-center flex-nowrap">
                      <Text fw="semibold" className={classes.vehicleName}>
                        {getVehicleDisplayName(vehicle)}
                      </Text>
                      <Text size="sm" c="dimmed">
                        {getVehicleYear(vehicle)}
                      </Text>
                    </div>
                    <div className="flex gap-2 flex-nowrap">
                      {vehicle.color && (
                        <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-[--color-bg-muted] text-[--color-text-muted]">
                          {vehicle.color}
                        </span>
                      )}
                      {vehicle.generation && (
                        <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-[--color-bg-muted] text-[--color-text-muted]">
                          {vehicle.generation}
                        </span>
                      )}
                      {vehicle.mileage != null && (
                        <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-[--color-bg-muted] text-[--color-text-muted]">
                          {vehicle.mileage.toLocaleString('ru-RU')} км
                        </span>
                      )}
                    </div>
                  </Stack>
                </div>
                <div className="flex gap-2 items-center">
                  <Button
                    variant="ghost"
                    size="xs"
                    className={classes.editButton}
                    onClick={() =>
                      navigate(`${routes.garage}/edit/${vehicle.id}`)
                    }
                  >
                    Редактировать
                  </Button>
                  <Button
                    variant="danger"
                    size="xs"
                    onClick={() => handleDeleteClick(vehicle)}
                  >
                    Удалить
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </Stack>
      )}

      <Dialog.Root open={deleteModalOpened} onOpenChange={setDeleteModalOpened}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 bg-black/50 z-40" />
          <Dialog.Content className="fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2 w-full max-w-md rounded-lg bg-[--color-surface] p-6 shadow-xl">
            <Dialog.Title className="text-lg font-semibold text-[--color-text] mb-4">
              Удалить автомобиль
            </Dialog.Title>
            <Stack gap="md">
              <Text>
                Вы уверены, что хотите удалить{' '}
                {vehicleToDelete && getVehicleDisplayName(vehicleToDelete)} из
                гаража?
              </Text>
              <Text size="sm" c="dimmed">
                Это действие нельзя отменить. Все данные об автомобиле будут
                удалены.
              </Text>
              <div className="flex justify-end gap-3">
                <Button variant="ghost" onClick={closeDeleteModal}>
                  Отмена
                </Button>
                <Button variant="danger" onClick={handleConfirmDelete}>
                  Удалить
                </Button>
              </div>
            </Stack>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  );
};

function getVehicleCountWord(count: number): string {
  const lastTwoDigits = count % 100;
  const lastDigit = count % 10;

  if (lastTwoDigits >= 11 && lastTwoDigits <= 14) {
    return 'автомобилей';
  }
  if (lastDigit === 1) {
    return 'автомобиль';
  }
  if (lastDigit >= 2 && lastDigit <= 4) {
    return 'автомобиля';
  }
  return 'автомобилей';
}

export default GaragePage;
