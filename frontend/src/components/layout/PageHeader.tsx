import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';
import type { MascotPageVariant } from '@/config/mascot';
import { LoopyMascot } from '@/components/mascot/LoopyMascot';

type Props = {
  title: string;
  /** One or two short sentences: what this page is for and what to do here. */
  description: string;
  /** Optional controls on the same row as the title (e.g. iteration selector). */
  titleAddon?: ReactNode;
  /** Loopy illustration for this page area. */
  mascot?: MascotPageVariant;
  className?: string;
};

/**
 * Page section title + lead text (below the site header in the main column).
 */
export function PageHeader({ title, description, titleAddon, mascot, className }: Props) {
  return (
    <header className={cn('space-y-2', className)}>
      <div className="flex flex-col gap-4 sm:flex-row sm:flex-wrap sm:items-start sm:justify-between sm:gap-4">
        <div className="min-w-0 flex-1 space-y-2">
          <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center sm:gap-3">
            <h2 className="text-xl font-semibold tracking-tight">{title}</h2>
            {titleAddon}
          </div>
          <p className="text-sm text-muted-foreground leading-relaxed max-w-3xl">{description}</p>
        </div>
        {mascot ? (
          <div className="shrink-0 flex justify-center sm:justify-end sm:pt-0.5">
            <LoopyMascot variant={mascot} />
          </div>
        ) : null}
      </div>
    </header>
  );
}
