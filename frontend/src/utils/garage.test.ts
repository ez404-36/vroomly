import { describe, it, expect } from 'vitest';
import type { ReminderDetailSchema } from '../api/vehiclesApi';
import type {
  UserVehicleListSchema,
  UserVehicleDetailSchema,
} from '../api/vehiclesApi';
import {
  formatReminderDate,
  reminderToInitialValue,
  getVehicleCountWord,
  combineDateAndTime,
  getVehicleDisplayName,
  buildVehicleCharacteristics,
} from './garage';

function makeVehicle(
  overrides: Partial<UserVehicleListSchema> = {},
): UserVehicleListSchema {
  return {
    id: 'veh-1',
    brand: 'Toyota',
    series: 'Corolla',
    generation: null,
    mileage: null,
    isMileageInMiles: false,
    ...overrides,
  } as UserVehicleListSchema;
}

function makeReminder(
  overrides: Partial<ReminderDetailSchema>,
): ReminderDetailSchema {
  return {
    id: 'rem-1',
    userVehicleId: 'veh-1',
    title: 'Замена масла',
    description: null,
    dueAt: null,
    isAllDay: false,
    isCompleted: false,
    completedAt: null,
    createdAt: '2026-01-01T00:00:00Z',
    updatedAt: null,
    ...overrides,
  };
}

describe('formatReminderDate', () => {
  it('returns an empty string for null/undefined/empty input', () => {
    expect(formatReminderDate(null)).toBe('');
    expect(formatReminderDate(undefined)).toBe('');
    expect(formatReminderDate('')).toBe('');
  });

  it('formats an ISO date as dd.mm.yyyy (ru-RU)', () => {
    // Midday UTC avoids any local-timezone day rollover.
    expect(formatReminderDate('2026-06-15T12:00:00Z')).toBe('15.06.2026');
  });

  it('pads single-digit day and month with leading zeros', () => {
    expect(formatReminderDate('2026-03-05T12:00:00Z')).toBe('05.03.2026');
  });
});

describe('reminderToInitialValue', () => {
  it('maps title and description (null description becomes empty string)', () => {
    const result = reminderToInitialValue(
      makeReminder({ title: 'Шиномонтаж', description: null }),
    );
    expect(result.title).toBe('Шиномонтаж');
    expect(result.description).toBe('');
    expect(result.allDay).toBe(false);
  });

  it('preserves a non-null description', () => {
    const result = reminderToInitialValue(
      makeReminder({ description: 'каждые 10 000 км' }),
    );
    expect(result.description).toBe('каждые 10 000 км');
  });

  it('leaves date and time null when there is no dueAt', () => {
    const result = reminderToInitialValue(makeReminder({ dueAt: null }));
    expect(result.date).toBeNull();
    expect(result.time).toBeNull();
  });

  it('sets date but not time for an all-day reminder', () => {
    const result = reminderToInitialValue(
      makeReminder({ dueAt: '2026-06-15T08:30:00Z', isAllDay: true }),
    );
    expect(result.date).toBeInstanceOf(Date);
    expect(result.time).toBeNull();
    expect(result.allDay).toBe(true);
  });

  it('derives a zero-padded HH:MM time for a timed reminder', () => {
    // Build the dueAt from a local Date so getHours()/getMinutes() are
    // timezone-independent in the assertion below.
    const local = new Date(2026, 5, 15, 7, 5); // 07:05 local time
    const result = reminderToInitialValue(
      makeReminder({ dueAt: local.toISOString(), isAllDay: false }),
    );
    expect(result.date).toBeInstanceOf(Date);
    expect(result.time).toBe('07:05');
  });
});

describe('getVehicleCountWord', () => {
  it('uses "автомобиль" for numbers ending in 1 (but not 11)', () => {
    expect(getVehicleCountWord(1)).toBe('автомобиль');
    expect(getVehicleCountWord(21)).toBe('автомобиль');
    expect(getVehicleCountWord(101)).toBe('автомобиль');
  });

  it('uses "автомобиля" for numbers ending in 2-4 (but not 12-14)', () => {
    expect(getVehicleCountWord(2)).toBe('автомобиля');
    expect(getVehicleCountWord(3)).toBe('автомобиля');
    expect(getVehicleCountWord(4)).toBe('автомобиля');
    expect(getVehicleCountWord(22)).toBe('автомобиля');
  });

  it('uses "автомобилей" for 0, 5-9 and the 11-14 exception range', () => {
    expect(getVehicleCountWord(0)).toBe('автомобилей');
    expect(getVehicleCountWord(5)).toBe('автомобилей');
    expect(getVehicleCountWord(9)).toBe('автомобилей');
    expect(getVehicleCountWord(11)).toBe('автомобилей');
    expect(getVehicleCountWord(12)).toBe('автомобилей');
    expect(getVehicleCountWord(13)).toBe('автомобилей');
    expect(getVehicleCountWord(14)).toBe('автомобилей');
    expect(getVehicleCountWord(111)).toBe('автомобилей');
  });
});

describe('combineDateAndTime', () => {
  it('returns null when there is no date', () => {
    expect(combineDateAndTime(null, '10:30', false)).toBeNull();
    expect(combineDateAndTime(null, null, true)).toBeNull();
  });

  it('applies HH:MM time for a timed reminder', () => {
    const result = combineDateAndTime(new Date(2026, 5, 15), '07:05', false);
    expect(result).not.toBeNull();
    expect(result?.getHours()).toBe(7);
    expect(result?.getMinutes()).toBe(5);
  });

  it('sets midnight for an all-day reminder (ignores time)', () => {
    const result = combineDateAndTime(new Date(2026, 5, 15), '07:05', true);
    expect(result?.getHours()).toBe(0);
    expect(result?.getMinutes()).toBe(0);
  });

  it('sets midnight when no time is provided', () => {
    const result = combineDateAndTime(new Date(2026, 5, 15), null, false);
    expect(result?.getHours()).toBe(0);
  });

  it('does not mutate the input date', () => {
    const input = new Date(2026, 5, 15, 12, 0);
    combineDateAndTime(input, '07:05', false);
    expect(input.getHours()).toBe(12);
  });
});

describe('getVehicleDisplayName', () => {
  it('joins brand, series and generation', () => {
    const name = getVehicleDisplayName(
      makeVehicle({ brand: 'Skoda', series: 'Octavia', generation: 'III' }),
    );
    expect(name).toBe('Skoda Octavia III');
  });

  it('skips empty parts', () => {
    const name = getVehicleDisplayName(
      makeVehicle({ brand: 'Skoda', series: 'Octavia', generation: null }),
    );
    expect(name).toBe('Skoda Octavia');
  });

  it('falls back when nothing is set', () => {
    const name = getVehicleDisplayName(
      makeVehicle({ brand: null, series: null, generation: null }),
    );
    expect(name).toBe('Неизвестное ТС');
  });
});

describe('buildVehicleCharacteristics', () => {
  it('returns an empty list when no fields are present', () => {
    expect(buildVehicleCharacteristics(makeVehicle(), null)).toEqual([]);
  });

  it('formats mileage with locale and km/miles unit', () => {
    const result = buildVehicleCharacteristics(
      makeVehicle({ mileage: 54321, isMileageInMiles: false }),
      null,
    );
    const mileage = result.find((c) => c.label === 'Текущий пробег');
    expect(mileage?.value).toContain('км');
    expect(mileage?.value).not.toContain('миль');
  });

  it('uses "миль" when mileage is in miles', () => {
    const result = buildVehicleCharacteristics(
      makeVehicle({ mileage: 1000, isMileageInMiles: true }),
      null,
    );
    const mileage = result.find((c) => c.label === 'Текущий пробег');
    expect(mileage?.value).toContain('миль');
  });

  it('includes detail fields (trim, color, fuel) when present', () => {
    const detail = {
      trim: 'Ambition',
      color: 'Серебристый',
      avgFuelConsumption: 7.5,
    } as UserVehicleDetailSchema;
    const result = buildVehicleCharacteristics(makeVehicle(), detail);
    const labels = result.map((c) => c.label);
    expect(labels).toContain('Комплектация');
    expect(labels).toContain('Цвет');
    expect(labels).toContain('Средний расход');
    expect(result.find((c) => c.label === 'Средний расход')?.value).toContain(
      'л/100км',
    );
  });
});
