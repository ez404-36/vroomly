import { useState, useEffect, useCallback, useRef } from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { Title, Text, Stack, Button, Tabs, TabContent } from '../ui';
import { Carousel } from '../ui';
import { Link, useNavigate } from 'react-router-dom';
import { routes } from '../utils/routes';
import {
  useGetUserVehiclesQuery,
  useGetUserVehicleQuery,
  useUpdateUserVehicleMileageMutation,
  useDeleteUserVehicleMutation,
  useGetRemindersQuery,
  useCreateReminderMutation,
  useUpdateReminderMutation,
  useCompleteReminderMutation,
  useUncompleteReminderMutation,
  useDeleteReminderMutation,
  type UserVehicleListSchema,
  type ReminderDetailSchema,
} from '../api/vehiclesApi';
import {
  ReminderItem,
  RecommendationCard,
  VehicleCard,
  AddReminderModal,
  UpdateMileageModal,
} from '../components/GaragePage';
import type {
  ReminderFormValue,
  ReminderModalInitialValue,
} from '../components/GaragePage/AddReminderModal';
import { generateGarageMocks, type Recommendation } from '../mocks/garageMocks';
import { MockService } from '../mocks';
import classes from '../styles/pages/Garage.module.css';

function formatReminderDate(dueAt: string | null | undefined): string {
  if (!dueAt) {
    return '';
  }
  return new Date(dueAt).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

function reminderToInitialValue(
  reminder: ReminderDetailSchema,
): ReminderModalInitialValue {
  let date: Date | null = null;
  let time: string | null = null;
  if (reminder.dueAt) {
    const parsed = new Date(reminder.dueAt);
    date = parsed;
    if (!reminder.isAllDay) {
      const hours = String(parsed.getHours()).padStart(2, '0');
      const minutes = String(parsed.getMinutes()).padStart(2, '0');
      time = `${hours}:${minutes}`;
    }
  }
  return {
    title: reminder.title,
    description: reminder.description ?? '',
    date,
    time,
    allDay: reminder.isAllDay,
  };
}

const GaragePage = () => {
  const navigate = useNavigate();
  const { data: vehicles, isLoading, error } = useGetUserVehiclesQuery();
  const [deleteVehicle] = useDeleteUserVehicleMutation();
  const [updateMileage, { isLoading: isMileageUpdating }] =
    useUpdateUserVehicleMileageMutation();
  const [createReminder] = useCreateReminderMutation();
  const [updateReminder] = useUpdateReminderMutation();
  const [completeReminder] = useCompleteReminderMutation();
  const [uncompleteReminder] = useUncompleteReminderMutation();
  const [deleteReminder] = useDeleteReminderMutation();

  const [deleteModalOpened, setDeleteModalOpened] = useState(false);
  const [reminderModalOpened, setReminderModalOpened] = useState(false);
  const [reminderToEdit, setReminderToEdit] =
    useState<ReminderDetailSchema | null>(null);
  const [reminderToDelete, setReminderToDelete] =
    useState<ReminderDetailSchema | null>(null);
  const [remindersTab, setRemindersTab] = useState('active');
  const [mileageModalOpened, setMileageModalOpened] = useState(false);
  const [mileageError, setMileageError] = useState<string | null>(null);
  const [vehicleToDelete, setVehicleToDelete] =
    useState<UserVehicleListSchema | null>(null);
  const [selectedVehicleIndex, setSelectedVehicleIndex] = useState(0);

  // Mock recommendations state - dynamically generated per vehicle (out of scope for reminders feature)
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);

  const currentVehicle =
    vehicles && vehicles.length > 0 ? vehicles[selectedVehicleIndex] : null;
  const currentVehicleId = currentVehicle?.id ?? null;

  // Детальная информация по выбранному ТС (все характеристики)
  const { data: currentVehicleDetail, isFetching: isDetailFetching } =
    useGetUserVehicleQuery(currentVehicle?.id ?? '', {
      skip: !currentVehicle,
    });

  // Напоминания по выбранному ТС: активные и история (выполненные)
  const { data: activeReminders } = useGetRemindersQuery(
    { userVehicleId: currentVehicleId ?? '', isCompleted: false },
    { skip: !currentVehicleId },
  );
  const { data: completedReminders } = useGetRemindersQuery(
    { userVehicleId: currentVehicleId ?? '', isCompleted: true },
    { skip: !currentVehicleId },
  );

  const prevVehicleIdRef = useRef<string | null>(null);

  const generateMocksForVehicle = useCallback((vehicleId: string) => {
    if (prevVehicleIdRef.current !== vehicleId) {
      prevVehicleIdRef.current = vehicleId;
      if (!MockService.isEnabled()) {
        setRecommendations([]);
        return;
      }
      const { recommendations: newRecommendations } =
        generateGarageMocks(vehicleId);
      setRecommendations(newRecommendations);
    }
  }, []);

  // Update mocks when selected vehicle changes
  useEffect(() => {
    if (currentVehicle?.id) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      generateMocksForVehicle(currentVehicle.id);
    }
  }, [currentVehicle?.id, generateMocksForVehicle]);

  // Update selected vehicle index when vehicles load
  const prevVehiclesLengthRef = useRef<number>(0);
  useEffect(() => {
    if (
      vehicles &&
      vehicles.length > 0 &&
      selectedVehicleIndex >= vehicles.length
    ) {
      prevVehiclesLengthRef.current = vehicles.length;
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setSelectedVehicleIndex(vehicles.length - 1);
    }
  }, [vehicles, selectedVehicleIndex]);

  const handleDeleteClick = (vehicle: UserVehicleListSchema) => {
    setVehicleToDelete(vehicle);
    setDeleteModalOpened(true);
  };

  const handleUpdateMileageClick = () => {
    if (!currentVehicle) {
      return;
    }
    setMileageError(null);
    setMileageModalOpened(true);
  };

  const handleMileageSubmit = async (data: {
    mileage: number;
    isMileageInMiles: boolean;
  }) => {
    if (!currentVehicle) {
      return;
    }
    setMileageError(null);
    try {
      await updateMileage({
        userVehicleId: currentVehicle.id,
        body: {
          mileage: data.mileage,
          isMileageInMiles: data.isMileageInMiles,
        },
      }).unwrap();
      setMileageModalOpened(false);
    } catch {
      setMileageError('Не удалось обновить пробег. Попробуйте ещё раз.');
    }
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

  const handleReminderCheckedChange = async (id: string, checked: boolean) => {
    try {
      if (checked) {
        await completeReminder(id).unwrap();
      } else {
        await uncompleteReminder(id).unwrap();
      }
    } catch {
      // cache stays consistent via tags; a failed mutation simply does not update
    }
  };

  const handleReminderDelete = async (reminder: ReminderDetailSchema) => {
    // Выполненные напоминания удаляются сразу, невыполненные — с подтверждением.
    if (reminder.isCompleted) {
      try {
        await deleteReminder(reminder.id).unwrap();
      } catch {
        // ignore — list reflects server state via cache tags
      }
      return;
    }
    setReminderToDelete(reminder);
  };

  const handleConfirmReminderDelete = async () => {
    if (reminderToDelete) {
      try {
        await deleteReminder(reminderToDelete.id).unwrap();
      } catch {
        // ignore
      }
      setReminderToDelete(null);
    }
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
    setReminderToEdit(null);
    setReminderModalOpened(true);
  };

  const handleEditReminderClick = (reminder: ReminderDetailSchema) => {
    setReminderToEdit(reminder);
    setReminderModalOpened(true);
  };

  const handleSubmitReminder = async (value: ReminderFormValue) => {
    if (!currentVehicle) {
      return;
    }
    const dueAt = value.dateTime ? value.dateTime.toISOString() : null;
    const body = {
      title: value.title,
      description: value.description,
      dueAt,
      isAllDay: value.allDay,
    };
    try {
      if (reminderToEdit) {
        await updateReminder({ reminderId: reminderToEdit.id, body }).unwrap();
      } else {
        await createReminder({
          userVehicleId: currentVehicle.id,
          body,
        }).unwrap();
      }
      setReminderToEdit(null);
    } catch {
      // ignore — modal already closed by the form; cache stays in sync via tags
    }
  };

  const renderReminderList = (
    items: ReminderDetailSchema[] | undefined,
    emptyText: string,
  ) =>
    items && items.length > 0 ? (
      <div className={classes.remindersList}>
        {items.map((reminder) => (
          <ReminderItem
            key={reminder.id}
            id={reminder.id}
            text={reminder.title}
            date={formatReminderDate(reminder.dueAt)}
            checked={reminder.isCompleted}
            onCheckedChange={handleReminderCheckedChange}
            onEdit={() => handleEditReminderClick(reminder)}
            onDelete={() => handleReminderDelete(reminder)}
          />
        ))}
      </div>
    ) : (
      <Text size="sm" c="dimmed" className={classes.emptyText}>
        {emptyText}
      </Text>
    );

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
              {vehicles.map((vehicle) => {
                const isActive = vehicle.id === currentVehicle?.id;
                return (
                  <VehicleCard
                    key={vehicle.id}
                    vehicle={vehicle}
                    detail={isActive ? currentVehicleDetail : null}
                    isDetailLoading={isActive && isDetailFetching}
                    large
                    onEdit={(v) => navigate(`${routes.garage}/edit/${v.id}`)}
                    onDelete={handleDeleteClick}
                    onUpdateMileage={handleUpdateMileageClick}
                  />
                );
              })}
            </Carousel>
          </section>

          {/* Reminders Section - for current vehicle */}
          <section className={classes.section}>
            <Title order={4} className={classes.sectionTitle}>
              Напоминания
            </Title>
            <div className={classes.remindersContainer}>
              <Tabs
                value={remindersTab}
                onValueChange={setRemindersTab}
                tabs={[
                  { value: 'active', label: 'Активные' },
                  { value: 'history', label: 'История' },
                ]}
              >
                <TabContent value="active">
                  {renderReminderList(
                    activeReminders,
                    'Нет активных напоминаний для этого автомобиля',
                  )}
                </TabContent>
                <TabContent value="history">
                  {renderReminderList(
                    completedReminders,
                    'История напоминаний пуста',
                  )}
                </TabContent>
              </Tabs>
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

      <Dialog.Root
        open={reminderToDelete !== null}
        onOpenChange={(open) => {
          if (!open) {
            setReminderToDelete(null);
          }
        }}
      >
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 bg-black/50 z-40" />
          <Dialog.Content className="fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2 w-full max-w-md rounded-lg bg-(--color-surface) p-6 shadow-xl">
            <Dialog.Title className="text-lg font-semibold text-(--color-text) mb-4">
              Удалить напоминание
            </Dialog.Title>
            <Stack gap="md">
              <Text>
                Вы уверены, что хотите удалить напоминание
                {reminderToDelete && ` «${reminderToDelete.title}»`}?
              </Text>
              <Text size="sm" c="dimmed">
                Напоминание ещё не выполнено. Это действие нельзя отменить.
              </Text>
              <div className="flex justify-end gap-3">
                <Button
                  variant="ghost"
                  onClick={() => setReminderToDelete(null)}
                >
                  Отмена
                </Button>
                <Button variant="danger" onClick={handleConfirmReminderDelete}>
                  Удалить
                </Button>
              </div>
            </Stack>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>

      <AddReminderModal
        open={reminderModalOpened}
        onOpenChange={setReminderModalOpened}
        onSubmit={handleSubmitReminder}
        mode={reminderToEdit ? 'edit' : 'create'}
        initialValue={
          reminderToEdit ? reminderToInitialValue(reminderToEdit) : null
        }
      />

      <UpdateMileageModal
        open={mileageModalOpened}
        onOpenChange={setMileageModalOpened}
        initialMileage={currentVehicle?.mileage ?? null}
        initialIsMileageInMiles={currentVehicle?.isMileageInMiles ?? false}
        isSubmitting={isMileageUpdating}
        error={mileageError}
        onSubmit={handleMileageSubmit}
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
