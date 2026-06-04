import { useState } from 'react';
import {
  useUpdateUserVehicleMileageMutation,
  type UserVehicleListSchema,
} from '../../api/vehiclesApi';

export interface MileageSubmitData {
  mileage: number;
  isMileageInMiles: boolean;
}

export interface UseMileageUpdateResult {
  isModalOpen: boolean;
  setModalOpen: (open: boolean) => void;
  isSubmitting: boolean;
  error: string | null;
  open: () => void;
  submit: (data: MileageSubmitData) => Promise<void>;
}

/**
 * Управление обновлением пробега выбранного ТС: состояние модалки, ошибка,
 * отправка мутации. Гард по `currentVehicle` — действия игнорируются, если ТС нет.
 */
export function useMileageUpdate(
  currentVehicle: UserVehicleListSchema | null,
): UseMileageUpdateResult {
  const [updateMileage, { isLoading: isSubmitting }] =
    useUpdateUserVehicleMileageMutation();
  const [isModalOpen, setModalOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const open = () => {
    if (!currentVehicle) {
      return;
    }
    setError(null);
    setModalOpen(true);
  };

  const submit = async (data: MileageSubmitData) => {
    if (!currentVehicle) {
      return;
    }
    setError(null);
    try {
      await updateMileage({
        userVehicleId: currentVehicle.id,
        body: {
          mileage: data.mileage,
          isMileageInMiles: data.isMileageInMiles,
        },
      }).unwrap();
      setModalOpen(false);
    } catch {
      setError('Не удалось обновить пробег. Попробуйте ещё раз.');
    }
  };

  return { isModalOpen, setModalOpen, isSubmitting, error, open, submit };
}
