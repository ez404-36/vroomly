import { Title, Text, Carousel } from '../../ui';
import { RecommendationCard } from './RecommendationCard';
import type { Recommendation } from '../../mocks/garageMocks';
import classes from '../../styles/pages/Garage.module.css';

interface RecommendationsSectionProps {
  recommendations: Recommendation[];
  onToggleChecked: (id: string, checked: boolean) => void;
}

/**
 * Секция рекомендаций по выбранному ТС (карусель карточек либо плейсхолдер).
 * Презентационный компонент.
 */
export function RecommendationsSection({
  recommendations,
  onToggleChecked,
}: RecommendationsSectionProps) {
  return (
    <section className={classes.section}>
      <Title order={4} className={classes.sectionTitle}>
        Рекомендации
      </Title>
      {recommendations.length > 0 ? (
        <Carousel className={classes.recommendationsCarousel}>
          {recommendations.map((rec) => (
            <RecommendationCard
              key={rec.id}
              title={rec.title}
              description={rec.description}
              checked={rec.checked}
              onCheckedChange={(checked) => onToggleChecked(rec.id, checked)}
            />
          ))}
        </Carousel>
      ) : (
        <Text size="sm" c="dimmed" className={classes.emptyText}>
          Нет рекомендаций для этого автомобиля
        </Text>
      )}
    </section>
  );
}
