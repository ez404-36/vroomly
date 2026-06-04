import type {
  ReminderDetailSchema,
  UserVehicleListSchema,
  UserVehicleDetailSchema,
} from '../api/vehiclesApi';
import type { ReminderModalInitialValue } from '../components/GaragePage/AddReminderModal';

export interface VehicleCharacteristic {
  label: string;
  value: string;
}

/**
 * Форматирует дату напоминания (ISO-строку) в локализованный вид `дд.мм.гггг`.
 * Возвращает пустую строку, если даты нет.
 */
export function formatReminderDate(dueAt: string | null | undefined): string {
  if (!dueAt) {
    return '';
  }
  return new Date(dueAt).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

/**
 * Преобразует напоминание из API в начальное значение формы модалки.
 *
 * Разбивает `dueAt` на дату и (для напоминаний с временем) строку `HH:MM`.
 * Для напоминаний «на весь день» время не выставляется.
 */
export function reminderToInitialValue(
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

/**
 * Собирает дату+время напоминания в единый `Date` (или `null`, если даты нет).
 *
 * Для «весь день» (или без указанного времени) ставит полночь. Иначе применяет
 * время из строки `HH:MM`. Чистая функция — не мутирует входной `date`.
 */
export function combineDateAndTime(
  date: Date | null,
  time: string | null,
  allDay: boolean,
): Date | null {
  if (!date) {
    return null;
  }
  const result = new Date(date);
  if (!allDay && time) {
    const [hours, minutes] = time.split(':');
    result.setHours(parseInt(hours, 10), parseInt(minutes, 10), 0, 0);
  } else {
    result.setHours(0, 0, 0, 0);
  }
  return result;
}

/**
 * Собирает отображаемое имя ТС из бренда/серии/поколения.
 * Возвращает запасной текст, если ничего не заполнено.
 */
export function getVehicleDisplayName(vehicle: UserVehicleListSchema): string {
  const parts = [vehicle.brand, vehicle.series, vehicle.generation].filter(
    Boolean,
  );
  return parts.length > 0 ? parts.join(' ') : 'Неизвестное ТС';
}

/**
 * Строит список характеристик ТС для карточки (комплектация, цвет, расход,
 * пробег) с локализованным форматированием чисел и единиц. Пропускает
 * отсутствующие поля. Чистая функция.
 */
export function buildVehicleCharacteristics(
  vehicle: UserVehicleListSchema,
  detail: UserVehicleDetailSchema | null | undefined,
): VehicleCharacteristic[] {
  const items: (VehicleCharacteristic | null)[] = [
    detail?.trim ? { label: 'Комплектация', value: detail.trim } : null,
    detail?.color ? { label: 'Цвет', value: detail.color } : null,
    detail?.avgFuelConsumption != null
      ? {
          label: 'Средний расход',
          value: `${detail.avgFuelConsumption.toLocaleString('ru-RU')} л/100км`,
        }
      : null,
    vehicle.mileage != null
      ? {
          label: 'Текущий пробег',
          value: `${vehicle.mileage.toLocaleString('ru-RU')} ${vehicle.isMileageInMiles ? 'миль' : 'км'}`,
        }
      : null,
  ];
  return items.filter((item): item is VehicleCharacteristic => item !== null);
}

/**
 * Возвращает правильную форму слова «автомобиль» для русской плюрализации
 * (1 автомобиль, 2 автомобиля, 5 автомобилей).
 */
export function getVehicleCountWord(count: number): string {
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
