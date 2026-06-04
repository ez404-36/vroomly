import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import type { ReminderDetailSchema } from '../../api/vehiclesApi';

const hoisted = vi.hoisted(() => ({
  createReminder: vi.fn(() => ({ unwrap: () => Promise.resolve(undefined) })),
  updateReminder: vi.fn(() => ({ unwrap: () => Promise.resolve(undefined) })),
  completeReminder: vi.fn(() => ({ unwrap: () => Promise.resolve(undefined) })),
  uncompleteReminder: vi.fn(() => ({
    unwrap: () => Promise.resolve(undefined),
  })),
  deleteReminder: vi.fn(() => ({ unwrap: () => Promise.resolve(undefined) })),
}));

vi.mock('../../api/vehiclesApi', () => ({
  useGetRemindersQuery: () => ({ data: [] }),
  useCreateReminderMutation: () => [hoisted.createReminder, {}],
  useUpdateReminderMutation: () => [hoisted.updateReminder, {}],
  useCompleteReminderMutation: () => [hoisted.completeReminder, {}],
  useUncompleteReminderMutation: () => [hoisted.uncompleteReminder, {}],
  useDeleteReminderMutation: () => [hoisted.deleteReminder, {}],
}));

import { useVehicleReminders } from './useVehicleReminders';

function makeReminder(
  overrides: Partial<ReminderDetailSchema> & {
    id: string;
    isCompleted: boolean;
  },
): ReminderDetailSchema {
  return {
    userVehicleId: 'veh-1',
    title: 'Замена масла',
    description: null,
    dueAt: null,
    isAllDay: false,
    completedAt: null,
    createdAt: '2026-01-01T00:00:00Z',
    updatedAt: null,
    ...overrides,
  };
}

describe('useVehicleReminders', () => {
  beforeEach(() => {
    Object.values(hoisted).forEach((fn) => fn.mockClear());
  });

  it('deletes a completed reminder immediately, without opening the dialog', () => {
    const { result } = renderHook(() => useVehicleReminders('veh-1'));

    act(() => {
      result.current.requestDelete(
        makeReminder({ id: 'done-1', isCompleted: true }),
      );
    });

    expect(hoisted.deleteReminder).toHaveBeenCalledWith('done-1');
    expect(result.current.reminderToDelete).toBeNull();
  });

  it('defers deletion of an active reminder until confirmation', async () => {
    const { result } = renderHook(() => useVehicleReminders('veh-1'));
    const active = makeReminder({ id: 'active-1', isCompleted: false });

    act(() => {
      result.current.requestDelete(active);
    });

    // Not deleted yet — awaiting confirmation.
    expect(hoisted.deleteReminder).not.toHaveBeenCalled();
    expect(result.current.reminderToDelete).toEqual(active);

    await act(async () => {
      await result.current.confirmDelete();
    });

    expect(hoisted.deleteReminder).toHaveBeenCalledWith('active-1');
    expect(result.current.reminderToDelete).toBeNull();
  });

  it('clears the pending delete request on cancel', () => {
    const { result } = renderHook(() => useVehicleReminders('veh-1'));

    act(() => {
      result.current.requestDelete(
        makeReminder({ id: 'active-2', isCompleted: false }),
      );
    });
    act(() => {
      result.current.clearDeleteRequest();
    });

    expect(result.current.reminderToDelete).toBeNull();
    expect(hoisted.deleteReminder).not.toHaveBeenCalled();
  });

  it('toggleCompleted calls complete/uncomplete based on the flag', async () => {
    const { result } = renderHook(() => useVehicleReminders('veh-1'));

    await act(async () => {
      await result.current.toggleCompleted('r1', true);
    });
    expect(hoisted.completeReminder).toHaveBeenCalledWith('r1');

    await act(async () => {
      await result.current.toggleCompleted('r1', false);
    });
    expect(hoisted.uncompleteReminder).toHaveBeenCalledWith('r1');
  });

  it('submit creates a reminder when not editing', async () => {
    const { result } = renderHook(() => useVehicleReminders('veh-1'));

    await act(async () => {
      await result.current.submit({
        title: 'Шиномонтаж',
        description: 'весна',
        dateTime: null,
        allDay: false,
      });
    });

    expect(hoisted.createReminder).toHaveBeenCalledWith({
      userVehicleId: 'veh-1',
      body: {
        title: 'Шиномонтаж',
        description: 'весна',
        dueAt: null,
        isAllDay: false,
      },
    });
    expect(hoisted.updateReminder).not.toHaveBeenCalled();
  });

  it('submit updates the reminder when editing', async () => {
    const { result } = renderHook(() => useVehicleReminders('veh-1'));
    const editing = makeReminder({ id: 'edit-1', isCompleted: false });

    act(() => {
      result.current.openEdit(editing);
    });
    await act(async () => {
      await result.current.submit({
        title: 'Новое',
        description: '',
        dateTime: null,
        allDay: false,
      });
    });

    expect(hoisted.updateReminder).toHaveBeenCalledWith({
      reminderId: 'edit-1',
      body: { title: 'Новое', description: '', dueAt: null, isAllDay: false },
    });
    expect(hoisted.createReminder).not.toHaveBeenCalled();
  });

  it('does not submit when there is no current vehicle', async () => {
    const { result } = renderHook(() => useVehicleReminders(null));

    await act(async () => {
      await result.current.submit({
        title: 'X',
        description: '',
        dateTime: null,
        allDay: false,
      });
    });

    expect(hoisted.createReminder).not.toHaveBeenCalled();
  });
});
