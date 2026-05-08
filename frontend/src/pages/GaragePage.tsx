import { useState } from 'react';
import {
  Title,
  Text,
  Card,
  Group,
  Stack,
  Badge,
  Button,
  Box,
  Modal,
  Skeleton,
  Alert,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { Link, useNavigate } from 'react-router-dom';
import { routes } from '../utils/routes';
import { useGetUserVehiclesQuery, useDeleteUserVehicleMutation } from '../api/vehiclesApi';
import { UserVehicleDetailSchema } from '../types/vehicleSchemas';
import classes from '../styles/pages/Garage.module.css';

const GaragePage = () => {
  const navigate = useNavigate();
  const { data: vehicles, isLoading, error } = useGetUserVehiclesQuery();
  const [deleteVehicle] = useDeleteUserVehicleMutation();
  const [deleteModalOpened, { open: openDeleteModal, close: closeDeleteModal }] = useDisclosure(false);
  const [vehicleToDelete, setVehicleToDelete] = useState<UserVehicleDetailSchema | null>(null);

  const handleDeleteClick = (vehicle: UserVehicleDetailSchema) => {
    setVehicleToDelete(vehicle);
    openDeleteModal();
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
    <Box className={classes.container}>
      <Box className={classes.header}>
        <Group justify="space-between" align="flex-start">
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
          <Button component={Link} to={routes.addVehicle} className={classes.addButton}>
            + Добавить ТС
          </Button>
        </Group>
      </Box>

      {isLoading && (
        <Stack gap="md">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} height={100} radius="md" />
          ))}
        </Stack>
      )}

      {error && (
        <Alert color="red" title="Ошибка загрузки">
          Не удалось загрузить список автомобилей
        </Alert>
      )}

      {!isLoading && !error && vehicles && vehicles.length === 0 && (
        <Card className={classes.emptyCard}>
          <Stack align="center" gap="md" py="xl">
            <Box className={classes.emptyIcon}>
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
            </Box>
            <Stack gap={4} align="center">
              <Text fw={600} size="lg">
                В гараже пока пусто
              </Text>
              <Text size="sm" c="dimmed" ta="center">
                Добавьте свой первый автомобиль, чтобы отслеживать его обслуживание и расходы
              </Text>
            </Stack>
            <Button component={Link} to={routes.addVehicle} size="md" className={classes.addButton}>
              + Добавить автомобиль
            </Button>
          </Stack>
        </Card>
      )}

      {!isLoading && !error && vehicles && vehicles.length > 0 && (
        <Stack gap="md" className={classes.vehiclesList}>
          {vehicles.map((vehicle) => (
            <Card key={vehicle.id} className={classes.vehicleCard} padding="lg">
              <Group justify="space-between" wrap="nowrap">
                <Group gap="md" wrap="nowrap" style={{ flex: 1 }}>
                  <Box className={classes.vehicleIcon}>
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
                  </Box>
                  <Stack gap={4} style={{ flex: 1 }}>
                    <Group gap="xs" wrap="nowrap">
                      <Text fw={600} className={classes.vehicleName}>
                        {getVehicleDisplayName(vehicle)}
                      </Text>
                      <Text size="sm" c="dimmed">
                        {getVehicleYear(vehicle)}
                      </Text>
                    </Group>
                    <Group gap="xs" wrap="nowrap">
                      {vehicle.color && (
                        <Badge variant="light" size="sm" color="gray">
                          {vehicle.color}
                        </Badge>
                      )}
                      {vehicle.generation && (
                        <Badge variant="light" size="sm" color="gray">
                          {vehicle.generation}
                        </Badge>
                      )}
                      {vehicle.mileage !== null && (
                        <Badge variant="light" size="sm" color="gray">
                          {vehicle.mileage.toLocaleString('ru-RU')} км
                        </Badge>
                      )}
                    </Group>
                  </Stack>
                </Group>
                <Group gap="xs">
                  <Button
                    variant="subtle"
                    size="xs"
                    className={classes.editButton}
                    onClick={() => navigate(`${routes.garage}/edit/${vehicle.id}`)}
                  >
                    Редактировать
                  </Button>
                  <Button
                    variant="subtle"
                    size="xs"
                    color="red"
                    onClick={() => handleDeleteClick(vehicle)}
                  >
                    Удалить
                  </Button>
                </Group>
              </Group>
            </Card>
          ))}
        </Stack>
      )}

      <Modal
        opened={deleteModalOpened}
        onClose={closeDeleteModal}
        title="Удалить автомобиль"
        centered
      >
        <Stack gap="md">
          <Text>
            Вы уверены, что хотите удалить {vehicleToDelete && getVehicleDisplayName(vehicleToDelete)} из гаража?
          </Text>
          <Text size="sm" c="dimmed">
            Это действие нельзя отменить. Все данные об автомобиле будут удалены.
          </Text>
          <Group justify="flex-end" gap="sm">
            <Button variant="subtle" onClick={closeDeleteModal}>
              Отмена
            </Button>
            <Button color="red" onClick={handleConfirmDelete}>
              Удалить
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Box>
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
