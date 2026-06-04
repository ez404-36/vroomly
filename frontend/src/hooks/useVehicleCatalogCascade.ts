import { useEffect, useMemo } from 'react';
import {
  useGetVehicleBrandsQuery,
  useGetVehicleSeriesQuery,
  useGetVehicleGenerationsQuery,
  useGetVehicleTrimsQuery,
  type GuessByVinResponseSchema,
} from '../api/vehiclesApi';
import {
  buildBrandOptions,
  buildSeriesOptions,
  buildGenerationOptions,
  buildTrimOptions,
  type SelectOption,
} from '../utils/vehicleOptions';

/** Какие из зависимых полей нужно очистить при каскадном сбросе. */
export interface CascadeReset {
  series?: boolean;
  generation?: boolean;
  trim?: boolean;
}

export interface UseVehicleCatalogCascadeArgs {
  /** Опциональное предзаполнение из guess_by_vin. */
  prefill?: GuessByVinResponseSchema;
  /** Текущая выбранная марка. */
  selectedBrand: string;
  /** Текущая выбранная модель/серия. */
  selectedSeries: string;
  /** Текущее выбранное поколение. */
  selectedGeneration: string;
  /**
   * Колбэк очистки зависимых полей формы. Вызывается из каскадных эффектов,
   * чтобы хук не зависел от конкретной реализации формы.
   */
  onResetFields: (fields: CascadeReset) => void;
}

export interface UseVehicleCatalogCascadeResult {
  brandOptions: SelectOption[];
  seriesOptions: SelectOption[];
  generationOptions: SelectOption[];
  trimOptions: SelectOption[];
  isSeriesLoading: boolean;
  isGenerationsLoading: boolean;
  isTrimsLoading: boolean;
}

/**
 * Инкапсулирует каталожный каскад марка→модель→поколение→комплектация:
 * 5 RTK Query запросов с условным skip, 3 производных override-флага
 * (prefill против API) и 3 каскадных эффекта очистки зависимых полей.
 * Построение опций селектов делегируется чистым функциям из
 * `utils/vehicleOptions`.
 *
 * Override-флаги выводятся из состояния (не хранятся в `useState`): пока
 * выбранное значение совпадает с соответствующим prefill-значением, опции
 * берутся из prefill, а запрос к API пропускается. Как только пользователь
 * меняет вышестоящее поле, override становится `false` и в дело вступают
 * данные API — без мутации состояния внутри эффектов.
 */
export function useVehicleCatalogCascade({
  prefill,
  selectedBrand,
  selectedSeries,
  selectedGeneration,
  onResetFields,
}: UseVehicleCatalogCascadeArgs): UseVehicleCatalogCascadeResult {
  const prefillBrandId = prefill?.brand.id ? String(prefill.brand.id) : '';
  const prefillSeriesId = prefill?.model.id ? String(prefill.model.id) : '';
  const prefillGenerationId =
    prefill?.generations && prefill.generations.length === 1
      ? String(prefill.generations[0].id)
      : '';

  // Override активен, пока выбранное значение совпадает с prefill по всей
  // вышестоящей цепочке: только тогда prefill-опции корректны для текущего выбора.
  const seriesOverride = Boolean(prefill) && selectedBrand === prefillBrandId;
  const generationOverride =
    seriesOverride && selectedSeries === prefillSeriesId;
  const trimOverride =
    generationOverride && selectedGeneration === prefillGenerationId;

  const { data: brands } = useGetVehicleBrandsQuery();

  const { data: seriesList, isLoading: isSeriesLoading } =
    useGetVehicleSeriesQuery(selectedBrand || '', {
      skip: !selectedBrand || seriesOverride,
    });

  const { data: generations, isLoading: isGenerationsLoading } =
    useGetVehicleGenerationsQuery(selectedSeries || '', {
      skip: !selectedSeries || generationOverride,
    });

  const { data: trims, isLoading: isTrimsLoading } = useGetVehicleTrimsQuery(
    selectedGeneration || '',
    { skip: !selectedGeneration || trimOverride },
  );

  // Каскадная очистка зависимых полей формы при сбросе вышестоящего значения.
  // Override-флаги выводятся напрямую из selected*, отдельная синхронизация не нужна.
  useEffect(() => {
    if (!selectedBrand) {
      onResetFields({ series: true, generation: true, trim: true });
    }
  }, [selectedBrand, onResetFields]);

  useEffect(() => {
    if (!selectedSeries) {
      onResetFields({ generation: true, trim: true });
    }
  }, [selectedSeries, onResetFields]);

  useEffect(() => {
    if (!selectedGeneration) {
      onResetFields({ trim: true });
    }
  }, [selectedGeneration, onResetFields]);

  const brandOptions = useMemo(
    () => buildBrandOptions(brands, prefill),
    [brands, prefill],
  );
  const seriesOptions = useMemo(
    () => buildSeriesOptions(seriesList, seriesOverride, prefill),
    [seriesList, seriesOverride, prefill],
  );
  const generationOptions = useMemo(
    () => buildGenerationOptions(generations, generationOverride, prefill),
    [generations, generationOverride, prefill],
  );
  const trimOptions = useMemo(
    () => buildTrimOptions(trims, trimOverride, prefill),
    [trims, trimOverride, prefill],
  );

  return {
    brandOptions,
    seriesOptions,
    generationOptions,
    trimOptions,
    isSeriesLoading,
    isGenerationsLoading,
    isTrimsLoading,
  };
}
