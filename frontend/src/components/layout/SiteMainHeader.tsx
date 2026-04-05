import { useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LoopyMascot } from '@/components/mascot/LoopyMascot';
import { pageChromeFromPath } from '@/config/pageChrome';
import { SITE_BROWSER_TAB_SUFFIX } from '@/config/site';

/**
 * Top of the main column: Loopy + current page title (replaces the old global long title + tagline).
 */
export function SiteMainHeader() {
  const { pathname } = useLocation();
  const { title, mascot } = pageChromeFromPath(pathname);

  useEffect(() => {
    document.title = `${title} · ${SITE_BROWSER_TAB_SUFFIX}`;
  }, [title]);

  return (
    <header className="mb-8 border-b border-border pb-6">
      <Link
        to="/"
        className="group flex items-center gap-3 rounded-sm outline-none ring-offset-background focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 sm:gap-4"
      >
        <span className="shrink-0 select-none pointer-events-none" aria-hidden>
          <LoopyMascot
            variant={mascot}
            maxHeightClass="max-h-16 sm:max-h-20"
            className="opacity-90 transition-opacity group-hover:opacity-100"
          />
        </span>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground transition-colors group-hover:text-primary sm:text-3xl">
          {title}
        </h1>
      </Link>
    </header>
  );
}
