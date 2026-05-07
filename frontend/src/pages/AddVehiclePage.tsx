import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Tabs, Container, Title, Stack, Button } from '@mantine/core';
import { VinLookupForm } from '../components/Vehicle/VinLookupForm';
import { VehicleForm } from '../components/Vehicle/VehicleForm';

export const AddVehiclePage = () => {
	const navigate = useNavigate();
	const [activeTab, setActiveTab] = useState<string | null>('vin');

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

				<Tabs value={activeTab} onChange={setActiveTab}>
					<Tabs.List>
						<Tabs.Tab value="vin">
							Через VIN
						</Tabs.Tab>
						<Tabs.Tab value="manual">
							Вручную
						</Tabs.Tab>
					</Tabs.List>

					<Tabs.Panel value="vin" pt="md">
						<VinLookupForm onSuccess={handleVinSuccess} />
					</Tabs.Panel>

					<Tabs.Panel value="manual" pt="md">
						<VehicleForm onSuccess={handleManualSuccess} />
					</Tabs.Panel>
				</Tabs>

				<Button variant="subtle" onClick={() => navigate(-1)}>
					Назад
				</Button>
			</Stack>
		</Container>
	);
};