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
      <div className="flex items-center gap-3 sm:gap-4">
        {mascot ? (
          <div className="shrink-0 flex select-none pointer-events-none" aria-hidden>
            <LoopyMascot
              variant={mascot}
              maxHeightClass="max-h-16 sm:max-h-20"
              className="opacity-[0.9]"
            />
          </div>
        ) : null}
        <div className="min-w-0 flex-1 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center sm:gap-3">
          <h2 className="text-xl font-semibold tracking-tight">{title}</h2>
          {titleAddon}
        </div>
      </div>
      <p className="text-sm text-muted-foreground leading-relaxed max-w-3xl">{description}</p>
    </header>
  );
}
