import { Link } from 'react-router-dom';
import { Stack, Text, Button } from '../../ui';
import { routes } from '../../utils/routes';
import classes from '../../styles/pages/Garage.module.css';

/**
 * Презентационный блок «пустого гаража»: иконка, пояснение и CTA-кнопка
 * добавления первого автомобиля.
 */
export function EmptyGarage() {
  return (
    <div className={classes.emptyCard}>
      <Stack align="center" gap="md">
        <div className={classes.emptyIcon}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1-.8-1.8-.8H5c-.6 0-1 .4-1 1v4c0 .6.4 1 1 1h2" />
            <circle cx="7" cy="17" r="2" />
            <circle cx="17" cy="17" r="2" />
            <path d="M14 17H9" />
            <path d="M5 10h14" />
          </svg>
        </div>
        <Stack gap={4} align="center">
          <Text fw="semibold" size="lg">
            В гараже пока пусто
          </Text>
          <Text size="sm" c="dimmed" ta="center">
            Добавьте свой первый автомобиль, чтобы отслеживать его обслуживание
            и расходы
          </Text>
        </Stack>
        <Link to={routes.addVehicle}>
          <Button size="md" className={classes.addButton}>
            + Добавить автомобиль
          </Button>
        </Link>
      </Stack>
    </div>
  );
}
