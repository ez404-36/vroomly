import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { ReminderDetailSchema } from '../types/schema-types';

/**
 * Tests for the core feature requirement (Phase H / plan):
 *   - Deleting a COMPLETED reminder happens immediately, with NO confirmation.
 *   - Deleting an ACTIVE (not completed) reminder requires confirmation first.
 *
 * We mock the data layer (vehiclesApi hooks), the router, and the mock-service
 * module so that the real GaragePage component logic (the delete branch and the
 * confirmation dialog) is exercised end-to-end without any network access.
 */

const hoisted = vi.hoisted(() => {
  const deleteReminderTrigger = vi.fn(() => ({
    unwrap: () => Promise.resolve(undefined),
  }));
  const noopMutationTrigger = vi.fn(() => ({
    unwrap: () => Promise.resolve(undefined),
  }));
  return {
    deleteReminderTrigger,
    noopMutationTrigger,
    // Mutable holders the tests configure before rendering.
    activeReminders: [] as ReminderDetailSchema[],
    completedReminders: [] as ReminderDetailSchema[],
  };
});

vi.mock('react-router-dom', () => ({
  useNavigate: () => vi.fn(),
  Link: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock('../mocks', () => ({
  MockService: { isEnabled: () => false },
}));

// Side-effect-only import in baseQuery; stub it to avoid a mocks<->baseQuery
// import cycle that leaves MockService undefined under the test runner.
vi.mock('../mocks/autoRegister', () => ({}));

vi.mock('../api/vehiclesApi', () => {
  const vehicle = {
    id: 'veh-1',
    brand: 'Toyota',
    series: 'Corolla',
    mileage: 1000,
    isMileageInMiles: false,
  };
  const mutation = () => [hoisted.noopMutationTrigger, {}];
  return {
    useGetUserVehiclesQuery: () => ({
      data: [vehicle],
      isLoading: false,
      error: undefined,
    }),
    useGetUserVehicleQuery: () => ({ data: null, isFetching: false }),
    useGetRemindersQuery: ({ isCompleted }: { isCompleted?: boolean }) => ({
      data: isCompleted ? hoisted.completedReminders : hoisted.activeReminders,
    }),
    useUpdateUserVehicleMileageMutation: () => [
      hoisted.noopMutationTrigger,
      { isLoading: false },
    ],
    useDeleteUserVehicleMutation: mutation,
    useCreateReminderMutation: mutation,
    useUpdateReminderMutation: mutation,
    useCompleteReminderMutation: mutation,
    useUncompleteReminderMutation: mutation,
    useDeleteReminderMutation: () => [hoisted.deleteReminderTrigger, {}],
  };
});

// Imported after the mocks above so GaragePage picks up the mocked modules.
import GaragePage from './GaragePage';

function makeReminder(
  overrides: Partial<ReminderDetailSchema> & {
    id: string;
    title: string;
    isCompleted: boolean;
  },
): ReminderDetailSchema {
  return {
    userVehicleId: 'veh-1',
    description: null,
    dueAt: null,
    isAllDay: false,
    completedAt: null,
    createdAt: '2026-01-01T00:00:00Z',
    updatedAt: null,
    ...overrides,
  };
}

describe('GaragePage — reminder delete confirmation rule', () => {
  beforeEach(() => {
    hoisted.deleteReminderTrigger.mockClear();
    hoisted.noopMutationTrigger.mockClear();
    hoisted.activeReminders = [];
    hoisted.completedReminders = [];
  });

  it('deletes a completed reminder immediately without a confirmation dialog', async () => {
    const user = userEvent.setup();
    hoisted.completedReminders = [
      makeReminder({ id: 'done-1', title: 'Выполненное', isCompleted: true }),
    ];

    render(<GaragePage />);

    // Switch to the history tab where completed reminders live.
    await user.click(screen.getByRole('tab', { name: 'История' }));

    const item = screen.getByText('Выполненное').closest('div');
    expect(item).not.toBeNull();
    const [, deleteButton] = within(item as HTMLElement).getAllByRole('button');
    await user.click(deleteButton);

    // Deleted right away, no confirmation dialog shown.
    expect(hoisted.deleteReminderTrigger).toHaveBeenCalledTimes(1);
    expect(hoisted.deleteReminderTrigger).toHaveBeenCalledWith('done-1');
    expect(screen.queryByText('Удалить напоминание')).not.toBeInTheDocument();
  });

  it('requires confirmation before deleting an active reminder', async () => {
    const user = userEvent.setup();
    hoisted.activeReminders = [
      makeReminder({ id: 'active-1', title: 'Активное', isCompleted: false }),
    ];

    render(<GaragePage />);

    const item = screen.getByText('Активное').closest('div');
    expect(item).not.toBeNull();
    const [, deleteButton] = within(item as HTMLElement).getAllByRole('button');
    await user.click(deleteButton);

    // Not deleted yet — a confirmation dialog must appear first.
    expect(hoisted.deleteReminderTrigger).not.toHaveBeenCalled();
    const dialog = await screen.findByRole('dialog');
    expect(within(dialog).getByText('Удалить напоминание')).toBeInTheDocument();

    // Confirm -> the reminder is deleted.
    await user.click(within(dialog).getByRole('button', { name: 'Удалить' }));
    expect(hoisted.deleteReminderTrigger).toHaveBeenCalledTimes(1);
    expect(hoisted.deleteReminderTrigger).toHaveBeenCalledWith('active-1');
  });

  it('does not delete an active reminder when the confirmation is cancelled', async () => {
    const user = userEvent.setup();
    hoisted.activeReminders = [
      makeReminder({ id: 'active-2', title: 'Отменяемое', isCompleted: false }),
    ];

    render(<GaragePage />);

    const item = screen.getByText('Отменяемое').closest('div');
    const [, deleteButton] = within(item as HTMLElement).getAllByRole('button');
    await user.click(deleteButton);

    const dialog = await screen.findByRole('dialog');
    await user.click(within(dialog).getByRole('button', { name: 'Отмена' }));

    expect(hoisted.deleteReminderTrigger).not.toHaveBeenCalled();
  });
});
