import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button, buttonVariants } from '@/components/ui/button';
import { LoopyMascot } from '@/components/mascot/LoopyMascot';
import { cn } from '@/lib/utils';
import { SITE_BROWSER_TAB_SUFFIX } from '@/config/site';

export type OopsLocationState = {
  message?: string;
};

/**
 * Minimal recovery UI: centered Loopy, title, and actions only.
 */
export function Oops() {
  useEffect(() => {
    document.title = `Oops · ${SITE_BROWSER_TAB_SUFFIX}`;
  }, []);

  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-8 text-center">
      <LoopyMascot
        variant="error"
        maxHeightClass="max-h-52 sm:max-h-64 md:max-h-72"
        className="opacity-95"
      />
      <h1 className="max-w-[20ch] text-balance text-3xl font-semibold tracking-tight sm:text-4xl md:text-5xl">
        Oops, something went wrong
      </h1>
      <div className="flex flex-wrap justify-center gap-3">
        <Button type="button" onClick={() => window.location.reload()}>
          Reload page
        </Button>
        <Link to="/" className={cn(buttonVariants({ variant: 'outline' }))}>
          Back to dashboard
        </Link>
      </div>
    </div>
  );
}
