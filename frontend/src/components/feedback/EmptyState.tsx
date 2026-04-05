import type { ReactNode } from 'react';
import type { MascotPageVariant } from '@/config/mascot';
import { LoopyMascot } from '@/components/mascot/LoopyMascot';

type Props = {
  /** Optional; main header already shows the page name. */
  title?: string;
  description: string;
  /** Loopy art; defaults to neutral empty pose. Pass `null` to hide. */
  mascot?: MascotPageVariant | null;
  children?: ReactNode;
};

export function EmptyState({ title, description, mascot = 'empty', children }: Props) {
  return (
    <div className="max-w-prose space-y-3">
      {title ? <h2 className="text-xl font-semibold">{title}</h2> : null}
      {mascot ? (
        <div className="py-1 select-none pointer-events-none" aria-hidden>
          <LoopyMascot
            variant={mascot}
            maxHeightClass="max-h-[6.5rem] sm:max-h-28"
            className="opacity-90"
          />
        </div>
      ) : null}
      <p className="text-muted-foreground">{description}</p>
      {children}
    </div>
  );
}
