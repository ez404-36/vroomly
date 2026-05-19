import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import * as Tabs from '@radix-ui/react-tabs';
import { Container, Title, Stack, Button } from '../ui';
import { VinLookupForm } from '../components/Vehicle/VinLookupForm';
import { VehicleForm } from '../components/Vehicle/VehicleForm';

export const AddVehiclePage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<string>('vin');

  const handleVinSuccess = () => {
    navigate('/garage');
  };

  const handleManualSuccess = () => {
    navigate('/garage');
  };

  return (
    <Container size="sm" py="xl">
      <Stack>
        <Title order={2}>Добавить транспортное средство</Title>

        <Tabs.Root value={activeTab} onValueChange={setActiveTab}>
          <Tabs.List className="flex gap-0 border-b border-[--color-border] mb-4">
            <Tabs.Trigger
              value="vin"
              className="px-4 py-2 text-sm font-medium text-[--color-text-muted] border-b-2 border-transparent data-[state=active]:border-[--color-primary] data-[state=active]:text-[--color-primary] transition-colors cursor-pointer"
            >
              Через VIN
            </Tabs.Trigger>
            <Tabs.Trigger
              value="manual"
              className="px-4 py-2 text-sm font-medium text-[--color-text-muted] border-b-2 border-transparent data-[state=active]:border-[--color-primary] data-[state=active]:text-[--color-primary] transition-colors cursor-pointer"
            >
              Вручную
            </Tabs.Trigger>
          </Tabs.List>

          <Tabs.Content value="vin" className="pt-2">
            <VinLookupForm onSuccess={handleVinSuccess} />
          </Tabs.Content>

          <Tabs.Content value="manual" className="pt-2">
            <VehicleForm onSuccess={handleManualSuccess} />
          </Tabs.Content>
        </Tabs.Root>

        <Button variant="ghost" onClick={() => navigate(-1)}>
          Назад
        </Button>
      </Stack>
    </Container>
  );
};
