import { useState } from 'react';
import {
  useGetRemindersQuery,
  useCreateReminderMutation,
  useUpdateReminderMutation,
  useCompleteReminderMutation,
  useUncompleteReminderMutation,
  useDeleteReminderMutation,
  type ReminderDetailSchema,
} from '../../api/vehiclesApi';
import type { ReminderFormValue } from '../../components/GaragePage/AddReminderModal';

export interface UseVehicleRemindersResult {
  activeReminders: ReminderDetailSchema[] | undefined;
  completedReminders: ReminderDetailSchema[] | undefined;
  /** Модалка создания/редактирования. */
  isModalOpen: boolean;
  setModalOpen: (open: boolean) => void;
  reminderToEdit: ReminderDetailSchema | null;
  openCreate: () => void;
  openEdit: (reminder: ReminderDetailSchema) => void;
  submit: (value: ReminderFormValue) => Promise<void>;
  /** complete/uncomplete по чекбоксу. */
  toggleCompleted: (id: string, checked: boolean) => Promise<void>;
  /** Удаление: выполненные — сразу, активные — через диалог подтверждения. */
  requestDelete: (reminder: ReminderDetailSchema) => void;
  reminderToDelete: ReminderDetailSchema | null;
  clearDeleteRequest: () => void;
  confirmDelete: () => Promise<void>;
}

/**
 * Управление напоминаниями выбранного ТС: активные/история, создание,
 * редактирование, отметка выполнения и удаление (с правилом «выполненные
 * удаляются сразу, активные — через подтверждение»).
 *
 * @param currentVehicleId id выбранного ТС; при `null` запросы пропускаются.
 */
export function useVehicleReminders(
  currentVehicleId: string | null,
): UseVehicleRemindersResult {
  const [createReminder] = useCreateReminderMutation();
  const [updateReminder] = useUpdateReminderMutation();
  const [completeReminder] = useCompleteReminderMutation();
  const [uncompleteReminder] = useUncompleteReminderMutation();
  const [deleteReminder] = useDeleteReminderMutation();

  const [isModalOpen, setModalOpen] = useState(false);
  const [reminderToEdit, setReminderToEdit] =
    useState<ReminderDetailSchema | null>(null);
  const [reminderToDelete, setReminderToDelete] =
    useState<ReminderDetailSchema | null>(null);

  const { data: activeReminders } = useGetRemindersQuery(
    { userVehicleId: currentVehicleId ?? '', isCompleted: false },
    { skip: !currentVehicleId },
  );
  const { data: completedReminders } = useGetRemindersQuery(
    { userVehicleId: currentVehicleId ?? '', isCompleted: true },
    { skip: !currentVehicleId },
  );

  const openCreate = () => {
    setReminderToEdit(null);
    setModalOpen(true);
  };

  const openEdit = (reminder: ReminderDetailSchema) => {
    setReminderToEdit(reminder);
    setModalOpen(true);
  };

  const submit = async (value: ReminderFormValue) => {
    if (!currentVehicleId) {
      return;
    }
    const body = {
      title: value.title,
      description: value.description,
      dueAt: value.dateTime ? value.dateTime.toISOString() : null,
      isAllDay: value.allDay,
    };
    try {
      if (reminderToEdit) {
        await updateReminder({ reminderId: reminderToEdit.id, body }).unwrap();
      } else {
        await createReminder({
          userVehicleId: currentVehicleId,
          body,
        }).unwrap();
      }
      setReminderToEdit(null);
    } catch {
      // Модалка уже закрыта формой; кэш синхронизируется через cache-теги.
    }
  };

  const toggleCompleted = async (id: string, checked: boolean) => {
    try {
      if (checked) {
        await completeReminder(id).unwrap();
      } else {
        await uncompleteReminder(id).unwrap();
      }
    } catch {
      // При ошибке мутация просто не применяется; список отражает сервер.
    }
  };

  const requestDelete = (reminder: ReminderDetailSchema) => {
    // Выполненные напоминания удаляются сразу, активные — с подтверждением.
    if (reminder.isCompleted) {
      void deleteReminder(reminder.id)
        .unwrap()
        .catch(() => {
          // ignore — список отражает состояние сервера через cache-теги
        });
      return;
    }
    setReminderToDelete(reminder);
  };

  const clearDeleteRequest = () => setReminderToDelete(null);

  const confirmDelete = async () => {
    if (!reminderToDelete) {
      return;
    }
    try {
      await deleteReminder(reminderToDelete.id).unwrap();
    } catch {
      // ignore
    }
    setReminderToDelete(null);
  };

  return {
    activeReminders,
    completedReminders,
    isModalOpen,
    setModalOpen,
    reminderToEdit,
    openCreate,
    openEdit,
    submit,
    toggleCompleted,
    requestDelete,
    reminderToDelete,
    clearDeleteRequest,
    confirmDelete,
  };
}
