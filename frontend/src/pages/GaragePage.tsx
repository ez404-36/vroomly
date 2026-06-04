import { Title, Text, Stack, Button, Carousel } from '../ui';
import { Link, useNavigate } from 'react-router-dom';
import { routes } from '../utils/routes';
import {
  VehicleCard,
  AddReminderModal,
  UpdateMileageModal,
  ConfirmDeleteDialog,
  EmptyGarage,
  RemindersSection,
  RecommendationsSection,
} from '../components/GaragePage';
import {
  useGarageVehicles,
  useVehicleReminders,
  useMileageUpdate,
  useGarageRecommendations,
} from '../hooks/garage';
import { reminderToInitialValue, getVehicleCountWord } from '../utils/garage';
import classes from '../styles/pages/Garage.module.css';

const GaragePage = () => {
  const navigate = useNavigate();

  const garage = useGarageVehicles();
  const { currentVehicle, currentVehicleId } = garage;
  const reminders = useVehicleReminders(currentVehicleId);
  const mileage = useMileageUpdate(currentVehicle);
  const recommendations = useGarageRecommendations(currentVehicleId);

  const { vehicles, isLoading, isError } = garage;
  const hasVehicles = !isLoading && !isError && vehicles && vehicles.length > 0;
  const isEmpty = !isLoading && !isError && vehicles && vehicles.length === 0;

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

      {isError && (
        <div className="rounded-md border border-(--color-danger) bg-(--color-danger)/10 px-4 py-3 text-sm text-(--color-danger)">
          Не удалось загрузить список автомобилей
        </div>
      )}

      {isEmpty && <EmptyGarage />}

      {hasVehicles && (
        <>
          <section className={classes.section}>
            <Carousel
              className={classes.vehicleCarousel}
              singleItem
              onIndexChange={garage.setSelectedVehicleIndex}
              initialIndex={garage.selectedVehicleIndex}
            >
              {vehicles.map((vehicle) => {
                const isActive = vehicle.id === currentVehicle?.id;
                return (
                  <VehicleCard
                    key={vehicle.id}
                    vehicle={vehicle}
                    detail={isActive ? garage.currentVehicleDetail : null}
                    isDetailLoading={isActive && garage.isDetailFetching}
                    large
                    onEdit={(v) => navigate(`${routes.garage}/edit/${v.id}`)}
                    onDelete={garage.requestDelete}
                    onUpdateMileage={mileage.open}
                  />
                );
              })}
            </Carousel>
          </section>

          <RemindersSection
            activeReminders={reminders.activeReminders}
            completedReminders={reminders.completedReminders}
            onToggleCompleted={reminders.toggleCompleted}
            onEdit={reminders.openEdit}
            onDelete={reminders.requestDelete}
            onAdd={reminders.openCreate}
          />

          <RecommendationsSection
            recommendations={recommendations.recommendations}
            onToggleChecked={recommendations.toggleChecked}
          />
        </>
      )}

      <ConfirmDeleteDialog
        open={garage.isDeleteDialogOpen}
        onOpenChange={garage.setDeleteDialogOpen}
        title="Удалить автомобиль"
        body={
          <>
            Вы уверены, что хотите удалить{' '}
            {garage.vehicleToDelete &&
              `${garage.vehicleToDelete.brand} ${garage.vehicleToDelete.series}`}{' '}
            из гаража?
          </>
        }
        note="Это действие нельзя отменить. Все данные об автомобиле будут удалены."
        onConfirm={garage.confirmDelete}
      />

      <ConfirmDeleteDialog
        open={reminders.reminderToDelete !== null}
        onOpenChange={(open) => {
          if (!open) {
            reminders.clearDeleteRequest();
          }
        }}
        title="Удалить напоминание"
        body={
          <>
            Вы уверены, что хотите удалить напоминание
            {reminders.reminderToDelete &&
              ` «${reminders.reminderToDelete.title}»`}
            ?
          </>
        }
        note="Напоминание ещё не выполнено. Это действие нельзя отменить."
        onConfirm={reminders.confirmDelete}
      />

      <AddReminderModal
        open={reminders.isModalOpen}
        onOpenChange={reminders.setModalOpen}
        onSubmit={reminders.submit}
        mode={reminders.reminderToEdit ? 'edit' : 'create'}
        initialValue={
          reminders.reminderToEdit
            ? reminderToInitialValue(reminders.reminderToEdit)
            : null
        }
      />

      <UpdateMileageModal
        open={mileage.isModalOpen}
        onOpenChange={mileage.setModalOpen}
        initialMileage={currentVehicle?.mileage ?? null}
        initialIsMileageInMiles={currentVehicle?.isMileageInMiles ?? false}
        isSubmitting={mileage.isSubmitting}
        error={mileage.error}
        onSubmit={mileage.submit}
      />
    </div>
  );
};

export default GaragePage;
