import { useState, useEffect, useCallback, useRef } from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { Title, Text, Stack, Button } from '../ui';
import { Carousel } from '../ui';
import { Link, useNavigate } from 'react-router-dom';
import { routes } from '../utils/routes';
import {
  useGetUserVehiclesQuery,
  useDeleteUserVehicleMutation,
  type UserVehicleDetailSchema,
} from '../api/vehiclesApi';
import {
  ReminderItem,
  RecommendationCard,
  VehicleCard,
  AddReminderModal,
} from '../components/GaragePage';
import {
  generateGarageMocks,
  type Reminder,
  type Recommendation,
} from '../mocks/garageMocks';
import classes from '../styles/pages/Garage.module.css';

const GaragePage = () => {
  const navigate = useNavigate();
  const { data: vehicles, isLoading, error } = useGetUserVehiclesQuery();
  const [deleteVehicle] = useDeleteUserVehicleMutation();
  const [deleteModalOpened, setDeleteModalOpened] = useState(false);
  const [addReminderModalOpened, setAddReminderModalOpened] = useState(false);
  const [vehicleToDelete, setVehicleToDelete] =
    useState<UserVehicleDetailSchema | null>(null);
  const [selectedVehicleIndex, setSelectedVehicleIndex] = useState(0);

  // Mock reminders state - dynamically generated per vehicle
  const [reminders, setReminders] = useState<Reminder[]>([]);

  // Mock recommendations state - dynamically generated per vehicle
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);

// Generate mocks when vehicle changes
  const currentVehicle = vehicles && vehicles.length > 0 ? vehicles[selectedVehicleIndex] : null;

  const prevVehicleIdRef = useRef<string | null>(null);

  const generateMocksForVehicle = useCallback((vehicleId: string) => {
    if (prevVehicleIdRef.current !== vehicleId) {
      prevVehicleIdRef.current = vehicleId;
      const { reminders: newReminders, recommendations: newRecommendations } = generateGarageMocks(vehicleId);
      setReminders(newReminders);
      setRecommendations(newRecommendations);
    }
  }, []);

  // Update mocks when selected vehicle changes
  useEffect(() => {
    if (currentVehicle?.id) {
      generateMocksForVehicle(currentVehicle.id);
    }
    // eslint-disable-next-line react-hooks/set-state-in-effect
  }, [currentVehicle?.id, generateMocksForVehicle]);

  // Update selected vehicle index when vehicles load
  const prevVehiclesLengthRef = useRef<number>(0);
  useEffect(() => {
    if (vehicles && vehicles.length > 0 && selectedVehicleIndex >= vehicles.length) {
      prevVehiclesLengthRef.current = vehicles.length;
      setSelectedVehicleIndex(vehicles.length - 1);
    }
    // eslint-disable-next-line react-hooks/set-state-in-effect
  }, [vehicles, selectedVehicleIndex]);

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

  const handleReminderCheckedChange = (id: string, checked: boolean) => {
    setReminders((prev) =>
      prev.map((r) => (r.id === id ? { ...r, checked } : r)),
    );
  };

  const handleReminderDelete = (id: string) => {
    setReminders((prev) => prev.filter((r) => r.id !== id));
  };

  const handleRecommendationCheckedChange = (id: string, checked: boolean) => {
    setRecommendations((prev) =>
      prev.map((r) => (r.id === id ? { ...r, checked } : r)),
    );
  };

  const handleAddReminderClick = () => {
    if (!currentVehicle) {
      return;
    }
    setAddReminderModalOpened(true);
  };

  const handleAddReminder = (reminder: {
    title: string;
    description: string;
    dateTime: Date | null;
    allDay: boolean;
  }) => {
    if (!currentVehicle) {
      return;
    }
    const newId = String(Date.now());
    const dateStr = reminder.dateTime
      ? reminder.dateTime.toLocaleDateString('ru-RU', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
        })
      : '';
    setReminders((prev) => [
      ...prev,
      {
        id: newId,
        text: reminder.title,
        description: reminder.description,
        date: dateStr,
        checked: false,
        vehicleId: currentVehicle.id,
      },
    ]);
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
            <Button className={classes.addButton}>+ Добавить ТС</Button>
          </Link>
        </div>
      </div>

      {isLoading && (
        <Stack gap="md">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-24 rounded-md bg-(--color-bg-muted) animate-pulse"
            />
          ))}
        </Stack>
      )}

      {error && (
        <div className="rounded-md border border-(--color-danger) bg-(--color-danger)/10 px-4 py-3 text-sm text-(--color-danger)">
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
        <>
          {/* Vehicle Carousel - shows 1 vehicle at a time */}
          <section className={classes.section}>
            <Carousel
              className={classes.vehicleCarousel}
              singleItem
              onIndexChange={setSelectedVehicleIndex}
              initialIndex={selectedVehicleIndex}
            >
              {vehicles.map((vehicle) => (
                <VehicleCard
                  key={vehicle.id}
                  vehicle={vehicle}
                  large
                  onEdit={(v) => navigate(`${routes.garage}/edit/${v.id}`)}
                  onDelete={handleDeleteClick}
                />
              ))}
            </Carousel>
          </section>

          {/* Reminders Section - for current vehicle */}
          <section className={classes.section}>
            <Title order={4} className={classes.sectionTitle}>
              Напоминания
            </Title>
            <div className={classes.remindersContainer}>
              {reminders.length > 0 ? (
                <div className={classes.remindersList}>
                  {reminders.map((reminder) => (
                    <ReminderItem
                      key={reminder.id}
                      id={reminder.id}
                      text={reminder.text}
                      date={reminder.date}
                      checked={reminder.checked}
                      onCheckedChange={handleReminderCheckedChange}
                      onDelete={handleReminderDelete}
                    />
                  ))}
                </div>
              ) : (
                <Text size="sm" c="dimmed" className={classes.emptyText}>
                  Нет напоминаний для этого автомобиля
                </Text>
              )}
              <Button
                variant="filled"
                size="sm"
                className={classes.addReminderButton}
                onClick={handleAddReminderClick}
              >
                + Напоминание
              </Button>
            </div>
          </section>

          {/* Recommendations Section - for current vehicle */}
          <section className={classes.section}>
            <Title order={4} className={classes.sectionTitle}>
              Рекомендации
            </Title>
            {recommendations.length > 0 ? (
              <Carousel className={classes.recommendationsCarousel}>
                {recommendations.map((rec) => (
                  <RecommendationCard
                    key={rec.id}
                    title={rec.title}
                    description={rec.description}
                    checked={rec.checked}
                    onCheckedChange={(checked) =>
                      handleRecommendationCheckedChange(rec.id, checked)
                    }
                  />
                ))}
              </Carousel>
            ) : (
              <Text size="sm" c="dimmed" className={classes.emptyText}>
                Нет рекомендаций для этого автомобиля
              </Text>
            )}
          </section>
        </>
      )}

      <Dialog.Root open={deleteModalOpened} onOpenChange={setDeleteModalOpened}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 bg-black/50 z-40" />
          <Dialog.Content className="fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2 w-full max-w-md rounded-lg bg-(--color-surface) p-6 shadow-xl">
            <Dialog.Title className="text-lg font-semibold text-(--color-text) mb-4">
              Удалить автомобиль
            </Dialog.Title>
            <Stack gap="md">
              <Text>
                Вы уверены, что хотите удалить{' '}
                {vehicleToDelete &&
                  `${vehicleToDelete.brand} ${vehicleToDelete.series}`}{' '}
                из гаража?
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

      <AddReminderModal
        open={addReminderModalOpened}
        onOpenChange={setAddReminderModalOpened}
        onAdd={handleAddReminder}
      />
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
