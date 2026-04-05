import type { ReactNode } from 'react';
import type { MascotPageVariant } from '@/config/mascot';
import { LoopyMascot } from '@/components/mascot/LoopyMascot';

type Props = {
  title: string;
  description: string;
  /** Loopy art; defaults to neutral empty pose. Pass `null` to hide. */
  mascot?: MascotPageVariant | null;
  children?: ReactNode;
};

export function EmptyState({ title, description, mascot = 'empty', children }: Props) {
  return (
    <div className="space-y-4">
      {mascot ? (
        <div className="flex justify-center sm:justify-start">
          <LoopyMascot variant={mascot} maxHeightClass="max-h-36" />
        </div>
      ) : null}
      <div className="space-y-2">
        <h2 className="text-xl font-semibold">{title}</h2>
        <p className="text-muted-foreground max-w-prose">{description}</p>
        {children}
      </div>
    </div>
  );
}
