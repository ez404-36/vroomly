import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import type { UserVehicleListSchema } from '../../api/vehiclesApi';

const hoisted = vi.hoisted(() => ({
  updateMileage: vi.fn(() => ({ unwrap: () => Promise.resolve(undefined) })),
}));

vi.mock('../../api/vehiclesApi', () => ({
  useUpdateUserVehicleMileageMutation: () => [
    hoisted.updateMileage,
    { isLoading: false },
  ],
}));

import { useMileageUpdate } from './useMileageUpdate';

const vehicle: UserVehicleListSchema = {
  id: 'veh-1',
  brand: 'Toyota',
  series: 'Corolla',
  mileage: 1000,
  isMileageInMiles: false,
} as UserVehicleListSchema;

describe('useMileageUpdate', () => {
  beforeEach(() => {
    hoisted.updateMileage.mockClear();
    hoisted.updateMileage.mockImplementation(() => ({
      unwrap: () => Promise.resolve(undefined),
    }));
  });

  it('open() does nothing when there is no current vehicle', () => {
    const { result } = renderHook(() => useMileageUpdate(null));
    act(() => result.current.open());
    expect(result.current.isModalOpen).toBe(false);
  });

  it('open() opens the modal and clears any prior error', () => {
    const { result } = renderHook(() => useMileageUpdate(vehicle));
    act(() => result.current.open());
    expect(result.current.isModalOpen).toBe(true);
    expect(result.current.error).toBeNull();
  });

  it('submit() sends the mutation and closes the modal on success', async () => {
    const { result } = renderHook(() => useMileageUpdate(vehicle));
    act(() => result.current.open());

    await act(async () => {
      await result.current.submit({ mileage: 54321, isMileageInMiles: true });
    });

    expect(hoisted.updateMileage).toHaveBeenCalledWith({
      userVehicleId: 'veh-1',
      body: { mileage: 54321, isMileageInMiles: true },
    });
    expect(result.current.isModalOpen).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('submit() sets an error message and keeps the modal open on failure', async () => {
    hoisted.updateMileage.mockImplementation(() => ({
      unwrap: () => Promise.reject(new Error('boom')),
    }));
    const { result } = renderHook(() => useMileageUpdate(vehicle));
    act(() => result.current.open());

    await act(async () => {
      await result.current.submit({ mileage: 1, isMileageInMiles: false });
    });

    expect(result.current.error).toBe(
      'Не удалось обновить пробег. Попробуйте ещё раз.',
    );
    expect(result.current.isModalOpen).toBe(true);
  });

  it('submit() does nothing when there is no current vehicle', async () => {
    const { result } = renderHook(() => useMileageUpdate(null));
    await act(async () => {
      await result.current.submit({ mileage: 1, isMileageInMiles: false });
    });
    expect(hoisted.updateMileage).not.toHaveBeenCalled();
  });
});
