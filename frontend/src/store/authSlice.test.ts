import { describe, it, expect, beforeEach } from 'vitest';
import reducer, { setAuthenticated, loginSucceeded, logout } from './authSlice';

describe('authSlice', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('loginSucceeded persists the token and marks authenticated', () => {
    const state = reducer(
      { isAuthenticated: false },
      loginSucceeded('jwt-token'),
    );
    expect(state.isAuthenticated).toBe(true);
    expect(localStorage.getItem('access_token')).toBe('jwt-token');
  });

  it('logout clears the token and marks unauthenticated', () => {
    localStorage.setItem('access_token', 'jwt-token');
    const state = reducer({ isAuthenticated: true }, logout());
    expect(state.isAuthenticated).toBe(false);
    expect(localStorage.getItem('access_token')).toBeNull();
  });

  it('setAuthenticated toggles the flag without touching storage', () => {
    const state = reducer({ isAuthenticated: false }, setAuthenticated(true));
    expect(state.isAuthenticated).toBe(true);
    expect(localStorage.getItem('access_token')).toBeNull();
  });
});
