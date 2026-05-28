import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Title, Stack } from '../ui';
import { VinLookupForm } from '../components/Vehicle/VinLookupForm';
import { VehicleForm } from '../components/Vehicle/VehicleForm';
import type { GuessByVinResponseSchema } from '../api/vehiclesApi';

type Step = 'vin' | 'form';

export const AddVehiclePage = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<Step>('vin');
  const [prefill, setPrefill] = useState<GuessByVinResponseSchema | undefined>(
    undefined,
  );

  const handleGuess = (data: GuessByVinResponseSchema) => {
    setPrefill(data);
    setStep('form');
  };

  const handleSkipToManual = () => {
    setPrefill(undefined);
    setStep('form');
  };

  const handleBackToVin = () => {
    setStep('vin');
  };

  const handleSuccess = () => {
    navigate('/garage');
  };

  return (
    <Container size="md" py="xl">
      <Stack>
        <Title order={2}>Добавить транспортное средство</Title>

        {step === 'vin' && (
          <VinLookupForm
            onGuess={handleGuess}
            onBack={() => navigate(-1)}
            onSkipToManual={handleSkipToManual}
          />
        )}

        {step === 'form' && (
          <VehicleForm
            prefill={prefill}
            onSuccess={handleSuccess}
            onBack={handleBackToVin}
          />
        )}
      </Stack>
    </Container>
  );
};
