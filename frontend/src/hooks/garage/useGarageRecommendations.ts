import { useState, useEffect, useCallback, useRef } from 'react';
import {
  generateGarageMocks,
  type Recommendation,
} from '../../mocks/garageMocks';
import { MockService } from '../../mocks';

export interface UseGarageRecommendationsResult {
  recommendations: Recommendation[];
  toggleChecked: (id: string, checked: boolean) => void;
}

/**
 * Mock-рекомендации по выбранному ТС (вне зоны фичи напоминаний).
 *
 * Рекомендации регенерируются только при смене `currentVehicleId`. Если
 * mock-режим выключен — список пуст. Логика моков изолирована в этом хуке,
 * чтобы не засорять страницу и держать `eslint-disable` локально.
 */
export function useGarageRecommendations(
  currentVehicleId: string | null,
): UseGarageRecommendationsResult {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const prevVehicleIdRef = useRef<string | null>(null);

  const generateForVehicle = useCallback((vehicleId: string) => {
    if (prevVehicleIdRef.current === vehicleId) {
      return;
    }
    prevVehicleIdRef.current = vehicleId;
    if (!MockService.isEnabled()) {
      setRecommendations([]);
      return;
    }
    const { recommendations: next } = generateGarageMocks(vehicleId);
    setRecommendations(next);
  }, []);

  useEffect(() => {
    if (currentVehicleId) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      generateForVehicle(currentVehicleId);
    }
  }, [currentVehicleId, generateForVehicle]);

  const toggleChecked = (id: string, checked: boolean) => {
    setRecommendations((prev) =>
      prev.map((r) => (r.id === id ? { ...r, checked } : r)),
    );
  };

  return { recommendations, toggleChecked };
}
