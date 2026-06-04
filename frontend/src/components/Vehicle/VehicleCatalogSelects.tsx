import { Select } from '../../ui';
import type { SelectOption } from '../../utils/vehicleOptions';

export interface VehicleCatalogSelectsProps {
  brandOptions: SelectOption[];
  seriesOptions: SelectOption[];
  generationOptions: SelectOption[];
  trimOptions: SelectOption[];
  selectedBrand: string;
  selectedSeries: string;
  selectedGeneration: string;
  selectedTrim: string;
  isSeriesLoading: boolean;
  isGenerationsLoading: boolean;
  isTrimsLoading: boolean;
  errors: {
    brandId?: string;
    seriesId?: string;
    generationId?: string;
    trimId?: string;
  };
  onBrandChange: (value: string) => void;
  onSeriesChange: (value: string) => void;
  onGenerationChange: (value: string) => void;
  onTrimChange: (value: string) => void;
}

/**
 * Презентационный блок четырёх каскадных селектов
 * (марка→модель→поколение→комплектация). Вся логика загрузки и построения
 * опций живёт в `useVehicleCatalogCascade`; здесь только рендер и проброс
 * значений/хендлеров.
 */
export const VehicleCatalogSelects = ({
  brandOptions,
  seriesOptions,
  generationOptions,
  trimOptions,
  selectedBrand,
  selectedSeries,
  selectedGeneration,
  selectedTrim,
  isSeriesLoading,
  isGenerationsLoading,
  isTrimsLoading,
  errors,
  onBrandChange,
  onSeriesChange,
  onGenerationChange,
  onTrimChange,
}: VehicleCatalogSelectsProps) => {
  return (
    <>
      <Select
        label="Марка"
        required
        placeholder="Выберите марку автомобиля"
        options={brandOptions}
        searchable
        clearable
        onChange={(value) => onBrandChange(value || '')}
        value={selectedBrand || ''}
        error={errors.brandId}
      />

      <Select
        key={`series-${selectedBrand}`}
        label="Модель"
        required
        placeholder="Выберите модель"
        options={seriesOptions}
        searchable
        clearable
        disabled={!selectedBrand || isSeriesLoading}
        onChange={(value) => onSeriesChange(value || '')}
        value={selectedSeries || ''}
        error={errors.seriesId}
      />

      <Select
        key={`generation-${selectedSeries}`}
        label="Поколение"
        placeholder="Выберите поколение"
        options={generationOptions}
        searchable
        clearable
        disabled={!selectedSeries || isGenerationsLoading}
        onChange={(value) => onGenerationChange(value || '')}
        value={selectedGeneration || ''}
        error={errors.generationId}
      />

      <Select
        key={`trim-${selectedGeneration}`}
        label="Комплектация"
        placeholder="Выберите комплектацию (опционально)"
        options={trimOptions}
        searchable
        clearable
        disabled={!selectedGeneration || isTrimsLoading}
        onChange={(value) => onTrimChange(value || '')}
        value={selectedTrim || ''}
        error={errors.trimId}
      />
    </>
  );
};
