import { describe, it, expect, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ConfirmDeleteDialog } from './ConfirmDeleteDialog';

describe('ConfirmDeleteDialog', () => {
  it('renders title, body and note when open', () => {
    render(
      <ConfirmDeleteDialog
        open
        onOpenChange={vi.fn()}
        title="Удалить автомобиль"
        body="Точно удалить Toyota Corolla?"
        note="Это действие нельзя отменить."
        onConfirm={vi.fn()}
      />,
    );

    const dialog = screen.getByRole('dialog');
    expect(within(dialog).getByText('Удалить автомобиль')).toBeInTheDocument();
    expect(
      within(dialog).getByText('Точно удалить Toyota Corolla?'),
    ).toBeInTheDocument();
    expect(
      within(dialog).getByText('Это действие нельзя отменить.'),
    ).toBeInTheDocument();
  });

  it('does not render content when closed', () => {
    render(
      <ConfirmDeleteDialog
        open={false}
        onOpenChange={vi.fn()}
        title="Удалить автомобиль"
        body="Точно?"
        onConfirm={vi.fn()}
      />,
    );

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('omits the note when not provided', () => {
    render(
      <ConfirmDeleteDialog
        open
        onOpenChange={vi.fn()}
        title="Удалить"
        body="Точно?"
        onConfirm={vi.fn()}
      />,
    );

    const dialog = screen.getByRole('dialog');
    // Only the body Text is present besides the title/buttons.
    expect(within(dialog).getByText('Точно?')).toBeInTheDocument();
  });

  it('uses default confirm/cancel labels', () => {
    render(
      <ConfirmDeleteDialog
        open
        onOpenChange={vi.fn()}
        title="Удалить"
        body="Точно?"
        onConfirm={vi.fn()}
      />,
    );

    const dialog = screen.getByRole('dialog');
    expect(
      within(dialog).getByRole('button', { name: 'Удалить' }),
    ).toBeInTheDocument();
    expect(
      within(dialog).getByRole('button', { name: 'Отмена' }),
    ).toBeInTheDocument();
  });

  it('calls onConfirm when the confirm button is clicked', async () => {
    const onConfirm = vi.fn();
    const user = userEvent.setup();
    render(
      <ConfirmDeleteDialog
        open
        onOpenChange={vi.fn()}
        title="Удалить"
        body="Точно?"
        confirmLabel="Удалить"
        onConfirm={onConfirm}
      />,
    );

    await user.click(screen.getByRole('button', { name: 'Удалить' }));
    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it('calls onOpenChange(false) when the cancel button is clicked', async () => {
    const onOpenChange = vi.fn();
    const user = userEvent.setup();
    render(
      <ConfirmDeleteDialog
        open
        onOpenChange={onOpenChange}
        title="Удалить"
        body="Точно?"
        onConfirm={vi.fn()}
      />,
    );

    await user.click(screen.getByRole('button', { name: 'Отмена' }));
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });
});
