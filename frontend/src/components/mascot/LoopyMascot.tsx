import { cn } from '@/lib/utils';
import type { MascotVariant } from '@/config/mascot';
import { mascotSrc } from '@/config/mascot';

type Props = {
  variant: MascotVariant;
  className?: string;
  /** Override default max height (Tailwind class). */
  maxHeightClass?: string;
};

/**
 * Loopy mascot figure from public static paths.
 */
export function LoopyMascot({ variant, className, maxHeightClass = 'max-h-28' }: Props) {
  return (
    <img
      src={mascotSrc(variant)}
      alt=""
      width={280}
      height={280}
      decoding="async"
      className={cn('w-auto object-contain opacity-95', maxHeightClass, className)}
      aria-hidden
    />
  );
}
