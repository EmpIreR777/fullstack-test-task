import { cn } from '@/lib/utils';

interface SpinnerProps {
  className?: string;
}

/** Нео-брутализм лоадер: три прыгающих «стикера». */
export function Spinner({ className }: SpinnerProps) {
  return (
    <span
      role="status"
      aria-label="Загрузка"
      className={cn('inline-flex items-end gap-1.5', className)}
    >
      <span className="size-2.5 animate-dot-bounce rounded-[4px] border-2 border-ink bg-lime" />
      <span className="size-2.5 animate-dot-bounce rounded-[4px] border-2 border-ink bg-sun [animation-delay:0.15s]" />
      <span className="size-2.5 animate-dot-bounce rounded-[4px] border-2 border-ink bg-coral [animation-delay:0.3s]" />
    </span>
  );
}
