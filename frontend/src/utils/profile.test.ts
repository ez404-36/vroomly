import { describe, it, expect } from 'vitest';
import { toProfileUpdatePayload, type ProfileFormData } from './profile';

function makeForm(overrides: Partial<ProfileFormData> = {}): ProfileFormData {
  return {
    login: 'user',
    email: 'user@example.com',
    name: 'Иван',
    surname: 'Иванов',
    birth_date: null,
    country_id: null,
    ...overrides,
  };
}

describe('toProfileUpdatePayload', () => {
  it('passes through non-empty name/surname and country_id', () => {
    const result = toProfileUpdatePayload(
      makeForm({ name: 'Иван', surname: 'Петров', country_id: 'c-1' }),
    );
    expect(result.name).toBe('Иван');
    expect(result.surname).toBe('Петров');
    expect(result.country_id).toBe('c-1');
  });

  it('normalizes empty-string name/surname to null', () => {
    const result = toProfileUpdatePayload(makeForm({ name: '', surname: '' }));
    expect(result.name).toBeNull();
    expect(result.surname).toBeNull();
  });

  it('formats birth_date as YYYY-MM-DD', () => {
    const result = toProfileUpdatePayload(
      makeForm({ birth_date: new Date(1990, 4, 15) }),
    );
    expect(result.birth_date).toBe('1990-05-15');
  });

  it('maps null birth_date to null', () => {
    const result = toProfileUpdatePayload(makeForm({ birth_date: null }));
    expect(result.birth_date).toBeNull();
  });

  it('does not include login/email in the payload', () => {
    const result = toProfileUpdatePayload(makeForm());
    expect(result).not.toHaveProperty('login');
    expect(result).not.toHaveProperty('email');
  });
});
