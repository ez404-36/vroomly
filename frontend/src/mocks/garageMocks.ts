/**
 * Mock data generators for GaragePage reminders and recommendations.
 * Generates vehicle-specific mock data that changes when vehicle selection changes.
 */

import { mockGenerators } from './mockService';

export interface Reminder {
  id: string;
  text: string;
  description: string;
  date: string;
  checked: boolean;
  vehicleId: string;
}

export interface Recommendation {
  id: string;
  title: string;
  description: string;
  checked: boolean;
  vehicleId: string;
}

// Reminder templates - various maintenance tasks
const REMINDER_TEMPLATES = [
  {
    text: 'Замена масла',
    description: 'Замена моторного масла и масляного фильтра',
  },
  {
    text: 'Замена воздушного фильтра',
    description: 'Проверка и замена воздушного фильтра двигателя',
  },
  {
    text: 'Замена тормозных колодок',
    description: 'Проверка состояния тормозных колодок',
  },
  {
    text: 'Проверка подвески',
    description: 'Диагностика ходовой части автомобиля',
  },
  {
    text: 'Замена охлаждающей жидкости',
    description: 'Промывка системы охлаждения',
  },
  {
    text: 'Проверка электрики',
    description: 'Диагностика электрооборудования',
  },
  {
    text: 'Замена свечей зажигания',
    description: 'Проверка и замена свечей зажигания',
  },
  {
    text: 'Регулировка развал-схождения',
    description: 'Проверка углов установки колёс',
  },
  {
    text: 'Чистка кондиционера',
    description: 'Дезинфекция и очистка системы кондиционирования',
  },
  { text: 'Проверка АКБ', description: 'Диагностика аккумуляторной батареи' },
];

// Recommendation templates - tips and suggestions
const RECOMMENDATION_TEMPLATES = [
  {
    title: 'Скоро ТО',
    description:
      'Пробег близок к очередному техобслуживанию. Рекомендуем пройти ТО в ближайшее время.',
  },
  {
    title: 'Проверьте давление',
    description: 'Давление в шинах не проверялось более 3 месяцев.',
  },
  {
    title: 'Обновите страховку',
    description: 'Полис ОСАГО или КАСКО истекает в ближайшее время.',
  },
  {
    title: 'Износ тормозов',
    description:
      'По данным диагностики, толщина тормозных колодок менее 30%. Рекомендуем замену.',
  },
  {
    title: 'Замена масла',
    description:
      'Рекомендуем заменить моторное масло. Пробег после последней замены превышает норму.',
  },
  {
    title: 'Сезонное ТО',
    description:
      'Подготовка к смене сезона. Проверьте систему отопления и кондиционирования.',
  },
  {
    title: 'Техосмотр',
    description: 'Близится срок прохождения технического осмотра.',
  },
  {
    title: 'Шины изношены',
    description:
      'Глубина протектора приближается к минимально допустимой. Рекомендуем замену.',
  },
];

function randomDate(daysFromNow: { min: number; max: number }): string {
  const today = new Date();
  const randomDays =
    Math.floor(Math.random() * (daysFromNow.max - daysFromNow.min + 1)) +
    daysFromNow.min;
  const date = new Date(today.getTime() + randomDays * 24 * 60 * 60 * 1000);
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

function generateVehicleSeed(vehicleId: string): number {
  let hash = 0;
  for (let i = 0; i < vehicleId.length; i++) {
    const char = vehicleId.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash;
  }
  return Math.abs(hash);
}

function seededRandom(seed: number): () => number {
  let s = seed;
  return () => {
    s = (s * 1103515245 + 12345) & 0x7fffffff;
    return s / 0x7fffffff;
  };
}

function shuffleWithSeed<T>(array: T[], seed: number): T[] {
  const rng = seededRandom(seed);
  const result = [...array];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

/**
 * Generate mock reminders for a specific vehicle.
 * Uses vehicle ID as seed for deterministic but unique data per vehicle.
 */
export function generateReminders(
  vehicleId: string,
  count: number = 3,
): Reminder[] {
  const seed = generateVehicleSeed(vehicleId);
  const shuffledTemplates = shuffleWithSeed(REMINDER_TEMPLATES, seed);
  const id = mockGenerators.uuid().slice(0, 8);

  return Array.from(
    { length: Math.min(count, shuffledTemplates.length) },
    (_, i) => {
      const template = shuffledTemplates[i];
      const reminderId = `${id}-${i + 1}`;
      const daysRange = i === 0 ? { min: 1, max: 14 } : { min: 7, max: 60 };

      return {
        id: reminderId,
        text: template.text,
        description: template.description,
        date: randomDate(daysRange),
        checked: false,
        vehicleId,
      };
    },
  );
}

/**
 * Generate mock recommendations for a specific vehicle.
 * Uses vehicle ID as seed for deterministic but unique data per vehicle.
 */
export function generateRecommendations(
  vehicleId: string,
  count: number = 3,
): Recommendation[] {
  const seed = generateVehicleSeed(vehicleId + '-rec');
  const shuffledTemplates = shuffleWithSeed(RECOMMENDATION_TEMPLATES, seed);
  const id = mockGenerators.uuid().slice(0, 8);

  return Array.from(
    { length: Math.min(count, shuffledTemplates.length) },
    (_, i) => {
      const template = shuffledTemplates[i];

      return {
        id: `${id}-${i + 1}`,
        title: template.title,
        description: template.description,
        checked: false,
        vehicleId,
      };
    },
  );
}

/**
 * Generate all mock data (reminders + recommendations) for a vehicle.
 */
export function generateGarageMocks(vehicleId: string): {
  reminders: Reminder[];
  recommendations: Recommendation[];
} {
  return {
    reminders: generateReminders(vehicleId, 3),
    recommendations: generateRecommendations(vehicleId, 3),
  };
}
