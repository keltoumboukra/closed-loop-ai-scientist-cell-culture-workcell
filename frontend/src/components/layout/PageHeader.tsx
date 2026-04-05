import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

type Props = {
  /** One or two short sentences: what this page is for and what to do here. */
  description: string;
  /** Optional controls (e.g. iteration selector on the iteration page). */
  titleAddon?: ReactNode;
  className?: string;
};

/**
 * Page lead text below the main Loopy + title header. No duplicate page title here.
 */
export function PageHeader({ description, titleAddon, className }: Props) {
  return (
    <header className={cn('space-y-3', className)}>
      {titleAddon ? (
        <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center sm:gap-3">
          {titleAddon}
        </div>
      ) : null}
      <p className="text-sm text-muted-foreground leading-relaxed max-w-3xl">{description}</p>
    </header>
  );
}
