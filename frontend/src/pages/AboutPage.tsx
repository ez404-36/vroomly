import { Stack, Text } from '../ui';
import classes from '../styles/pages/About.module.css';

const features = [
  {
    title: 'Учёт автомобилей',
    description:
      'Ведите учёт всех ваших транспортных средств в одном месте. Добавляйте марку, модель, год выпуска, пробег и другие параметры.',
    icon: (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
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
      </svg>
    ),
  },
  {
    title: 'Записи на сервис',
    description:
      'Планируйте техническое обслуживание и записывайтесь на сервис. Получайте уведомления о предстоящих ТО.',
    icon: (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
      </svg>
    ),
  },
  {
    title: 'Учёт расходов',
    description:
      'Отслеживайте все расходы на автомобиль: топливо, обслуживание, ремонт, страховка. Анализируйте затраты по категориям.',
    icon: (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <rect width="20" height="14" x="2" y="5" rx="2" />
        <line x1="2" x2="22" y1="10" y2="10" />
      </svg>
    ),
  },
  {
    title: 'История обслуживания',
    description:
      'Храните полную историю всех работ и обслуживаний. Вся информация всегда доступна и не потеряется.',
    icon: (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M12 8v4l3 3" />
        <circle cx="12" cy="12" r="10" />
      </svg>
    ),
  },
];

const benefits = [
  {
    title: 'Экономия времени',
    description:
      'Все данные об автомобиле всегда под рукой. Больше не нужно искать чеки и записи в разных местах.',
  },
  {
    title: 'Контроль расходов',
    description:
      'Видите полную картину затрат на автомобиль. Планируйте бюджет и оптимизируйте расходы.',
  },
  {
    title: 'Забота о здоровье авто',
    description:
      'Не пропускайте важные даты обслуживания. Вовремя выполненное ТО продлевает жизнь вашему автомобилю.',
  },
  {
    title: 'Безопасность данных',
    description:
      'Все данные надёжно хранятся в облаке. Получайте доступ к информации с любого устройства.',
  },
];

export const AboutPage = () => {
  return (
    <div className={classes.container}>
      <div className={classes.header}>
        <div className={classes.heroIcon}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="40"
            height="40"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
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
        <h1 className={classes.title}>О сервисе Vroomly</h1>
        <Text size="lg" c="dimmed" className={classes.subtitle}>
          Ваш персональный помощник по управлению автомобилем. Учёт, планирование
          и контроль — всё в одном месте.
        </Text>
      </div>

      <div className={classes.section}>
        <h2 className={classes.sectionTitle}>Возможности</h2>
        <div className={classes.featuresList}>
          {features.map((feature) => (
            <div key={feature.title} className={classes.featureCard}>
              <div className={classes.featureIcon}>{feature.icon}</div>
              <h3 className={classes.featureTitle}>{feature.title}</h3>
              <p className={classes.featureDescription}>{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      <div className={classes.section}>
        <h2 className={classes.sectionTitle}>Почему Vroomly</h2>
        <Stack gap="md" className={classes.benefitsList}>
          {benefits.map((benefit) => (
            <div key={benefit.title} className={classes.benefitItem}>
              <div className={classes.benefitIcon}>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              </div>
              <div className={classes.benefitContent}>
                <h4 className={classes.benefitTitle}>{benefit.title}</h4>
                <p className={classes.benefitDescription}>{benefit.description}</p>
              </div>
            </div>
          ))}
        </Stack>
      </div>

      <div className={classes.section}>
        <div className={classes.contactCard}>
          <h3 className={classes.contactTitle}>Техническая поддержка</h3>
          <Text size="sm" c="dimmed" className={classes.contactDescription}>
            Есть вопросы или предложения? Свяжитесь с нами, и мы поможем.
          </Text>
          <button type="button" className={classes.contactButton}>
            Написать в поддержку
          </button>
        </div>
      </div>
    </div>
  );
};