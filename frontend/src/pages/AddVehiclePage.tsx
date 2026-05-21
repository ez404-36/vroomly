import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Title, Stack, Tabs, TabContent } from '../ui';
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

        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          tabs={[
            { value: 'vin', label: 'Через VIN' },
            { value: 'manual', label: 'Вручную' },
          ]}
        >
          <TabContent value="vin" className="pt-2">
            <VinLookupForm
              onSuccess={handleVinSuccess}
              onBack={() => navigate(-1)}
            />
          </TabContent>

          <TabContent value="manual" className="pt-2">
            <VehicleForm
              onSuccess={handleManualSuccess}
              onBack={() => navigate(-1)}
            />
          </TabContent>
        </Tabs>
      </Stack>
    </Container>
  );
};
