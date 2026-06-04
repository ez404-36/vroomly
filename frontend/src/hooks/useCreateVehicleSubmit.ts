import type { SerializedError } from '@reduxjs/toolkit';
import type { FetchBaseQueryError } from '@reduxjs/toolkit/query/react';
import {
  useCreateUserVehicleMutation,
  type CreateUserVehicleSchema,
} from '../api/vehiclesApi';

export interface VehicleFormData {
  brandId: string;
  seriesId: string;
  generationId: string;
  trimId: string;
  productionYear: number | undefined;
  color: string;
  mileage: number | undefined;
  avgFuelConsumption: number | undefined;
  isMileageInMiles: boolean;
  vin: string;
}

/**
 * Преобразует данные формы ТС в payload создания.
 *
 * Возвращает `null`, если обязательный год выпуска не заполнен (вызывающий
 * прерывает сабмит). Пустые строки нормализуются в `null`, `undefined`
 * числовые — в `null`. Чистая функция — тестируется изолированно.
 */
export function toCreateVehiclePayload(
  data: VehicleFormData,
): CreateUserVehicleSchema | null {
  if (data.productionYear === undefined) {
    return null;
  }
  return {
    generationId: data.generationId || null,
    trimId: data.trimId || null,
    productionYear: data.productionYear,
    color: data.color || null,
    mileage: data.mileage ?? null,
    isMileageInMiles: data.isMileageInMiles,
    avgFuelConsumption: data.avgFuelConsumption ?? null,
    vin: data.vin || null,
  };
}

export interface UseCreateVehicleSubmitResult {
  isLoading: boolean;
  error: FetchBaseQueryError | SerializedError | undefined;
  submit: (data: VehicleFormData) => Promise<void>;
}

/**
 * Логика создания ТС: маппинг формы→payload + мутация + обработка ошибки.
 * При успехе вызывает `onSuccess`. Ошибка доступна вызывающему через `error`
 * (UI её отображает).
 *
 * @param onSuccess колбэк после успешного создания (например, навигация).
 */
export function useCreateVehicleSubmit(
  onSuccess?: () => void,
): UseCreateVehicleSubmitResult {
  const [createVehicle, { isLoading, error }] = useCreateUserVehicleMutation();

  const submit = async (data: VehicleFormData) => {
    const payload = toCreateVehiclePayload(data);
    if (!payload) {
      return;
    }
    try {
      await createVehicle(payload).unwrap();
      onSuccess?.();
    } catch {
      // Ошибка доступна вызывающему через `error`; UI её отображает.
    }
  };

  return { isLoading, error, submit };
}
