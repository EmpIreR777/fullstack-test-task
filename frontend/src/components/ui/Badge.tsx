import { cn } from '@/lib/utils';

type Variant = 'default' | 'success' | 'warning' | 'danger' | 'info';

interface BadgeProps {
  variant?: Variant;
  children: React.ReactNode;
  className?: string;
}

const variantClasses: Record<Variant, string> = {
  default: 'bg-white text-ink',
  success: 'bg-lime text-ink',
  warning: 'bg-sun text-ink',
  danger: 'bg-coral text-ink',
  info: 'bg-sky text-ink',
};

export function Badge({ variant = 'default', children, className }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border-2 border-ink px-2.5 py-0.5 text-[11px] font-bold uppercase tracking-wide shadow-brutal-xs',
        variantClasses[variant],
        className,
      )}
    >
      {children}
    </span>
  );
}
