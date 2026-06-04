import type {
  GuessByVinResponseSchema,
  VehicleBrandDetailSchema,
  VehicleSeriesListSchema,
  VehicleGenerationListSchema,
  VehicleTrimListSchema,
} from '../api/vehiclesApi';

export interface SelectOption {
  value: string;
  label: string;
}

/**
 * Строит опцию селекта из каталожной сущности с полями `id`/`name`.
 *
 * `id` приводится к строке: каталожные API возвращают строковые UUID, а
 * prefill из `guess_by_vin` — `string | number`, поэтому нормализуем единообразно.
 */
function toOption<T extends { id: string | number; name: string }>(
  item: T,
): SelectOption {
  return { value: String(item.id), label: item.name };
}

/**
 * Опции марок: список из API. Если задан `prefill`, его марка гарантированно
 * присутствует в списке (добавляется в начало, если её там ещё нет), чтобы
 * предвыбранное значение отображалось даже до загрузки полного каталога.
 */
export function buildBrandOptions(
  brands: VehicleBrandDetailSchema[] | undefined,
  prefill?: GuessByVinResponseSchema,
): SelectOption[] {
  const base = brands?.map(toOption) ?? [];
  if (!prefill) {
    return base;
  }
  const id = String(prefill.brand.id);
  if (base.some((opt) => opt.value === id)) {
    return base;
  }
  return [{ value: id, label: prefill.brand.name }, ...base];
}

/**
 * Опции моделей. Пока действует override из prefill — возвращает единственную
 * модель из prefill. Иначе строит опции из API-списка серий.
 */
export function buildSeriesOptions(
  seriesList: VehicleSeriesListSchema[] | undefined,
  seriesOverride: boolean,
  prefill?: GuessByVinResponseSchema,
): SelectOption[] {
  if (seriesOverride && prefill) {
    return [{ value: String(prefill.model.id), label: prefill.model.name }];
  }
  return seriesList?.map(toOption) ?? [];
}

/**
 * Опции поколений. При активном override из prefill — поколения из prefill,
 * иначе из API-списка.
 */
export function buildGenerationOptions(
  generations: VehicleGenerationListSchema[] | undefined,
  generationOverride: boolean,
  prefill?: GuessByVinResponseSchema,
): SelectOption[] {
  if (generationOverride && prefill) {
    return (
      prefill.generations?.map((g) => ({
        value: String(g.id),
        label: g.name,
      })) ?? []
    );
  }
  return generations?.map(toOption) ?? [];
}

/**
 * Опции комплектаций. При активном override из prefill — комплектации из
 * prefill с label `name — description` (description содержит двигатель/КПП/
 * привод/кузов, чтобы из селектора было понятно, какую комплектацию выбирают).
 * Иначе — опции из API-списка (только `name`).
 */
export function buildTrimOptions(
  trims: VehicleTrimListSchema[] | undefined,
  trimOverride: boolean,
  prefill?: GuessByVinResponseSchema,
): SelectOption[] {
  if (trimOverride && prefill) {
    return (
      prefill.trims?.map((t) => ({
        value: String(t.id),
        label: t.description ? `${t.name} — ${t.description}` : t.name,
      })) ?? []
    );
  }
  return trims?.map(toOption) ?? [];
}
