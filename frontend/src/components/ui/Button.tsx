import { type ComponentPropsWithoutRef } from 'react';
import { cn } from '@/lib/utils';

type Variant = 'primary' | 'secondary' | 'danger' | 'ghost';
type Size = 'sm' | 'md';

interface ButtonProps extends ComponentPropsWithoutRef<'button'> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
}

const pressEffect =
  'hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-brutal-sm active:translate-x-0 active:translate-y-0 active:shadow-none';

const variantClasses: Record<Variant, string> = {
  primary: `bg-lime text-ink shadow-brutal-xs ${pressEffect}`,
  secondary: `bg-white text-ink shadow-brutal-xs ${pressEffect}`,
  danger: `bg-coral text-ink shadow-brutal-xs ${pressEffect}`,
  ghost:
    'border-transparent bg-transparent text-ink/60 shadow-none hover:border-ink/15 hover:bg-ink/5 hover:text-ink',
};

const sizeClasses: Record<Size, string> = {
  sm: 'px-3.5 py-1.5 text-xs',
  md: 'px-5 py-2.5 text-sm',
};

export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled,
  className,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      disabled={disabled ?? loading}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-full border-2 border-ink font-bold uppercase tracking-wide transition-all duration-100',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink focus-visible:ring-offset-2 focus-visible:ring-offset-paper',
        'disabled:pointer-events-none disabled:opacity-40',
        variantClasses[variant],
        sizeClasses[size],
        className,
      )}
      {...props}
    >
      {loading ? (
        <svg
          className="size-4 shrink-0 animate-spin"
          viewBox="0 0 24 24"
          fill="none"
          aria-hidden="true"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8v4l3-3-3-3v4a10 10 0 100 10l-2-2a8 8 0 01-6-8z"
          />
        </svg>
      ) : (
        children
      )}
    </button>
  );
}
