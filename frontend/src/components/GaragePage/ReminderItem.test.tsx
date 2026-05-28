import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ReminderItem } from './ReminderItem';

function renderItem(
  overrides: Partial<Parameters<typeof ReminderItem>[0]> = {},
) {
  const props = {
    id: 'rem-1',
    text: 'Заменить масло',
    date: '01.06.2026',
    checked: false,
    onCheckedChange: vi.fn(),
    onEdit: vi.fn(),
    onDelete: vi.fn(),
    ...overrides,
  };
  render(<ReminderItem {...props} />);
  return props;
}

describe('ReminderItem', () => {
  it('renders the reminder text and date', () => {
    renderItem({ text: 'Поменять шины', date: '15.10.2026' });

    expect(screen.getByText('Поменять шины')).toBeInTheDocument();
    expect(screen.getByText('15.10.2026')).toBeInTheDocument();
  });

  it('renders the text without line-through styling when not completed', () => {
    renderItem({ text: 'Активное', checked: false });

    const text = screen.getByText('Активное');
    expect(text.className).not.toContain('line-through');
  });

  it('renders the text with line-through styling when completed', () => {
    renderItem({ text: 'Выполнено', checked: true });

    const text = screen.getByText('Выполнено');
    expect(text.className).toContain('line-through');
  });

  it('reflects the completed state on the checkbox', () => {
    renderItem({ checked: true });

    const checkbox = screen.getByRole('checkbox');
    expect(checkbox).toBeChecked();
  });

  it('calls onCheckedChange with id and new checked value when toggled', async () => {
    const user = userEvent.setup();
    const props = renderItem({ id: 'rem-42', checked: false });

    await user.click(screen.getByRole('checkbox'));

    expect(props.onCheckedChange).toHaveBeenCalledTimes(1);
    expect(props.onCheckedChange).toHaveBeenCalledWith('rem-42', true);
  });

  it('calls onEdit with the reminder id when the edit button is clicked', async () => {
    const user = userEvent.setup();
    const props = renderItem({ id: 'rem-7' });

    // ReminderItem renders exactly two buttons: edit (first), delete (second).
    const [editButton] = screen.getAllByRole('button');
    await user.click(editButton);

    expect(props.onEdit).toHaveBeenCalledTimes(1);
    expect(props.onEdit).toHaveBeenCalledWith('rem-7');
  });

  it('calls onDelete with the reminder id when the delete button is clicked', async () => {
    const user = userEvent.setup();
    const props = renderItem({ id: 'rem-9' });

    const [, deleteButton] = screen.getAllByRole('button');
    await user.click(deleteButton);

    expect(props.onDelete).toHaveBeenCalledTimes(1);
    expect(props.onDelete).toHaveBeenCalledWith('rem-9');
  });
});
