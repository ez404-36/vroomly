import { describe, it, expect } from 'vitest';
import type {
  GuessByVinResponseSchema,
  VehicleBrandDetailSchema,
  VehicleSeriesListSchema,
  VehicleGenerationListSchema,
  VehicleTrimListSchema,
} from '../api/vehiclesApi';
import {
  buildBrandOptions,
  buildSeriesOptions,
  buildGenerationOptions,
  buildTrimOptions,
} from './vehicleOptions';

function brand(
  overrides: Partial<VehicleBrandDetailSchema> = {},
): VehicleBrandDetailSchema {
  return {
    id: 'b-1',
    countryId: 'c-1',
    code: 'skoda',
    name: 'Skoda',
    originalName: null,
    ...overrides,
  };
}

function series(
  overrides: Partial<VehicleSeriesListSchema> = {},
): VehicleSeriesListSchema {
  return { id: 's-1', name: 'Octavia', brandId: 'b-1', ...overrides };
}

function generation(
  overrides: Partial<VehicleGenerationListSchema> = {},
): VehicleGenerationListSchema {
  return {
    id: 'g-1',
    name: 'III',
    seriesId: 's-1',
    startYear: 2013,
    endYear: null,
    ...overrides,
  };
}

function trim(
  overrides: Partial<VehicleTrimListSchema> = {},
): VehicleTrimListSchema {
  return { id: 't-1', name: 'Ambition', generationId: 'g-1', ...overrides };
}

function makePrefill(
  overrides: Partial<GuessByVinResponseSchema> = {},
): GuessByVinResponseSchema {
  return {
    brand: { id: 'pb-1', name: 'Audi' },
    model: { id: 'pm-1', name: 'A4' },
    generations: [{ id: 'pg-1', name: 'B9' }],
    trims: [
      {
        id: 'pt-1',
        name: 'Sport',
        parent: { id: 'pg-1', name: 'B9' },
        description: '2.0 TFSI · АКПП · Седан',
      },
    ],
    vin: 'WAUZZZ00000000000',
    year: 2020,
    color: 'Чёрный',
    ...overrides,
  };
}

describe('buildBrandOptions', () => {
  it('maps API brands to value/label (happy path)', () => {
    const result = buildBrandOptions([
      brand(),
      brand({ id: 'b-2', name: 'BMW' }),
    ]);
    expect(result).toEqual([
      { value: 'b-1', label: 'Skoda' },
      { value: 'b-2', label: 'BMW' },
    ]);
  });

  it('returns empty array for undefined brands and no prefill', () => {
    expect(buildBrandOptions(undefined)).toEqual([]);
  });

  it('prepends prefill brand when missing from API list (prefill-merge)', () => {
    const result = buildBrandOptions([brand()], makePrefill());
    expect(result[0]).toEqual({ value: 'pb-1', label: 'Audi' });
    expect(result).toHaveLength(2);
  });

  it('does not duplicate prefill brand already present in API list', () => {
    const prefill = makePrefill({ brand: { id: 'b-1', name: 'Skoda' } });
    const result = buildBrandOptions([brand()], prefill);
    expect(result).toEqual([{ value: 'b-1', label: 'Skoda' }]);
  });

  it('coerces numeric prefill brand id to string', () => {
    const prefill = makePrefill({ brand: { id: 42, name: 'Lada' } });
    const result = buildBrandOptions(undefined, prefill);
    expect(result).toEqual([{ value: '42', label: 'Lada' }]);
  });
});

describe('buildSeriesOptions', () => {
  it('maps API series when override is off (happy path)', () => {
    const result = buildSeriesOptions([series()], false, makePrefill());
    expect(result).toEqual([{ value: 's-1', label: 'Octavia' }]);
  });

  it('returns single prefill model when override is on', () => {
    const result = buildSeriesOptions([series()], true, makePrefill());
    expect(result).toEqual([{ value: 'pm-1', label: 'A4' }]);
  });

  it('returns empty array for undefined series and override off', () => {
    expect(buildSeriesOptions(undefined, false)).toEqual([]);
  });
});

describe('buildGenerationOptions', () => {
  it('maps API generations when override is off (happy path)', () => {
    const result = buildGenerationOptions([generation()], false, makePrefill());
    expect(result).toEqual([{ value: 'g-1', label: 'III' }]);
  });

  it('returns prefill generations when override is on', () => {
    const result = buildGenerationOptions(undefined, true, makePrefill());
    expect(result).toEqual([{ value: 'pg-1', label: 'B9' }]);
  });

  it('returns empty array when override on but prefill has no generations', () => {
    const prefill = makePrefill({ generations: undefined });
    expect(buildGenerationOptions(undefined, true, prefill)).toEqual([]);
  });

  it('returns empty array for undefined generations and override off', () => {
    expect(buildGenerationOptions(undefined, false)).toEqual([]);
  });
});

describe('buildTrimOptions', () => {
  it('maps API trims by name only when override is off (happy path)', () => {
    const result = buildTrimOptions([trim()], false, makePrefill());
    expect(result).toEqual([{ value: 't-1', label: 'Ambition' }]);
  });

  it('formats prefill trim label as "name — description" when override on', () => {
    const result = buildTrimOptions(undefined, true, makePrefill());
    expect(result).toEqual([
      { value: 'pt-1', label: 'Sport — 2.0 TFSI · АКПП · Седан' },
    ]);
  });

  it('falls back to name when prefill trim has empty description', () => {
    const prefill = makePrefill({
      trims: [
        {
          id: 'pt-2',
          name: 'Base',
          parent: { id: 'pg-1', name: 'B9' },
          description: '',
        },
      ],
    });
    const result = buildTrimOptions(undefined, true, prefill);
    expect(result).toEqual([{ value: 'pt-2', label: 'Base' }]);
  });

  it('returns empty array when override on but prefill has no trims', () => {
    const prefill = makePrefill({ trims: undefined });
    expect(buildTrimOptions(undefined, true, prefill)).toEqual([]);
  });

  it('returns empty array for undefined trims and override off', () => {
    expect(buildTrimOptions(undefined, false)).toEqual([]);
  });
});
