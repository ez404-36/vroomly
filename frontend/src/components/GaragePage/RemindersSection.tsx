import { useState } from 'react';
import { Title, Text, Button, Tabs, TabContent } from '../../ui';
import { ReminderItem } from './ReminderItem';
import type { ReminderDetailSchema } from '../../api/vehiclesApi';
import { formatReminderDate } from '../../utils/garage';
import classes from '../../styles/pages/Garage.module.css';

interface RemindersSectionProps {
  activeReminders: ReminderDetailSchema[] | undefined;
  completedReminders: ReminderDetailSchema[] | undefined;
  onToggleCompleted: (id: string, checked: boolean) => void;
  onEdit: (reminder: ReminderDetailSchema) => void;
  onDelete: (reminder: ReminderDetailSchema) => void;
  onAdd: () => void;
}

function ReminderList({
  items,
  emptyText,
  onToggleCompleted,
  onEdit,
  onDelete,
}: {
  items: ReminderDetailSchema[] | undefined;
  emptyText: string;
  onToggleCompleted: (id: string, checked: boolean) => void;
  onEdit: (reminder: ReminderDetailSchema) => void;
  onDelete: (reminder: ReminderDetailSchema) => void;
}) {
  if (!items || items.length === 0) {
    return (
      <Text size="sm" c="dimmed" className={classes.emptyText}>
        {emptyText}
      </Text>
    );
  }
  return (
    <div className={classes.remindersList}>
      {items.map((reminder) => (
        <ReminderItem
          key={reminder.id}
          id={reminder.id}
          text={reminder.title}
          date={formatReminderDate(reminder.dueAt)}
          checked={reminder.isCompleted}
          onCheckedChange={onToggleCompleted}
          onEdit={() => onEdit(reminder)}
          onDelete={() => onDelete(reminder)}
        />
      ))}
    </div>
  );
}

/**
 * Секция напоминаний выбранного ТС: вкладки «Активные»/«История», списки и
 * кнопка добавления. Презентационный компонент — вся логика приходит пропсами.
 */
export function RemindersSection({
  activeReminders,
  completedReminders,
  onToggleCompleted,
  onEdit,
  onDelete,
  onAdd,
}: RemindersSectionProps) {
  const [tab, setTab] = useState('active');

  return (
    <section className={classes.section}>
      <Title order={4} className={classes.sectionTitle}>
        Напоминания
      </Title>
      <div className={classes.remindersContainer}>
        <Tabs
          value={tab}
          onValueChange={setTab}
          tabs={[
            { value: 'active', label: 'Активные' },
            { value: 'history', label: 'История' },
          ]}
        >
          <TabContent value="active">
            <ReminderList
              items={activeReminders}
              emptyText="Нет активных напоминаний для этого автомобиля"
              onToggleCompleted={onToggleCompleted}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          </TabContent>
          <TabContent value="history">
            <ReminderList
              items={completedReminders}
              emptyText="История напоминаний пуста"
              onToggleCompleted={onToggleCompleted}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          </TabContent>
        </Tabs>
        <Button
          variant="filled"
          size="sm"
          className={classes.addReminderButton}
          onClick={onAdd}
        >
          + Напоминание
        </Button>
      </div>
    </section>
  );
}
