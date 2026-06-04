import { useState } from 'react';
import {
  useGetUserVehiclesQuery,
  useGetUserVehicleQuery,
  useDeleteUserVehicleMutation,
  type UserVehicleListSchema,
  type UserVehicleDetailSchema,
} from '../../api/vehiclesApi';

export interface UseGarageVehiclesResult {
  vehicles: UserVehicleListSchema[] | undefined;
  isLoading: boolean;
  isError: boolean;
  currentVehicle: UserVehicleListSchema | null;
  currentVehicleId: string | null;
  currentVehicleDetail: UserVehicleDetailSchema | undefined;
  isDetailFetching: boolean;
  selectedVehicleIndex: number;
  setSelectedVehicleIndex: (index: number) => void;
  /** Диалог удаления ТС. */
  vehicleToDelete: UserVehicleListSchema | null;
  isDeleteDialogOpen: boolean;
  requestDelete: (vehicle: UserVehicleListSchema) => void;
  setDeleteDialogOpen: (open: boolean) => void;
  confirmDelete: () => Promise<void>;
}

/**
 * Управление списком ТС гаража: выбор активного ТС, детальная информация,
 * корректировка индекса при изменении списка, удаление с подтверждением.
 *
 * Возвращает данные + действия для презентационных компонентов гаража.
 */
export function useGarageVehicles(): UseGarageVehiclesResult {
  const { data: vehicles, isLoading, error } = useGetUserVehiclesQuery();
  const [deleteVehicle] = useDeleteUserVehicleMutation();

  const [selectedVehicleIndex, setSelectedVehicleIndexRaw] = useState(0);
  const [vehicleToDelete, setVehicleToDelete] =
    useState<UserVehicleListSchema | null>(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  // Индекс может «протухнуть» после удаления последнего ТС — нормализуем при чтении,
  // не вызывая setState в эффекте (избегаем set-state-in-effect и лишних ререндеров).
  const clampedIndex =
    vehicles && vehicles.length > 0
      ? Math.min(selectedVehicleIndex, vehicles.length - 1)
      : 0;

  const currentVehicle =
    vehicles && vehicles.length > 0 ? vehicles[clampedIndex] : null;
  const currentVehicleId = currentVehicle?.id ?? null;

  const { data: currentVehicleDetail, isFetching: isDetailFetching } =
    useGetUserVehicleQuery(currentVehicleId ?? '', {
      skip: !currentVehicleId,
    });

  const requestDelete = (vehicle: UserVehicleListSchema) => {
    setVehicleToDelete(vehicle);
    setIsDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!vehicleToDelete) {
      return;
    }
    try {
      await deleteVehicle(vehicleToDelete.id).unwrap();
      setVehicleToDelete(null);
    } catch {
      // Список отражает состояние сервера через cache-теги; при ошибке просто
      // закрываем диалог без локального изменения.
    } finally {
      setIsDeleteDialogOpen(false);
    }
  };

  return {
    vehicles,
    isLoading,
    isError: Boolean(error),
    currentVehicle,
    currentVehicleId,
    currentVehicleDetail,
    isDetailFetching,
    selectedVehicleIndex: clampedIndex,
    setSelectedVehicleIndex: setSelectedVehicleIndexRaw,
    vehicleToDelete,
    isDeleteDialogOpen,
    requestDelete,
    setDeleteDialogOpen: setIsDeleteDialogOpen,
    confirmDelete,
  };
}
