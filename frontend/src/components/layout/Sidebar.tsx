import { Link, NavLink, useLocation } from 'react-router-dom';
import { ExternalLink, Github } from 'lucide-react';
import { cn } from '@/lib/utils';
import { GITHUB_REPO_URL } from '@/config/site';
import { LoopyMascot } from '@/components/mascot/LoopyMascot';

const navClass = ({ isActive }: { isActive: boolean }) =>
  cn(
    'block px-3 py-2 rounded-md text-sm transition-colors',
    isActive
      ? 'bg-primary text-primary-foreground font-medium'
      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
  );

/** Default iteration when opening "Iteration View" from the sidebar (first known id). */
const DEFAULT_ITERATION_PATH = '/iterations/iter_001';

export function Sidebar() {
  const { pathname } = useLocation();
  const iterationNavActive = pathname.startsWith('/iterations/');

  return (
    <aside className="w-56 shrink-0 border-r border-border bg-muted/40 flex flex-col">
      <div className="flex justify-center border-b border-border px-2 py-3">
        <Link
          to="/"
          className="rounded-md outline-none ring-offset-background focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          aria-label="Home"
        >
          <LoopyMascot variant="head" maxHeightClass="max-h-11" className="opacity-90" />
        </Link>
      </div>
      <nav className="flex-1 overflow-y-auto p-2 pt-3 space-y-1">
        <NavLink to="/" end className={navClass}>
          Dashboard
        </NavLink>
        <Link
          to={DEFAULT_ITERATION_PATH}
          className={cn(
            'block px-3 py-2 rounded-md text-sm transition-colors',
            iterationNavActive
              ? 'bg-primary text-primary-foreground font-medium'
              : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
          )}
        >
          Iteration View
        </Link>
        <NavLink to="/history" end className={navClass}>
          History
        </NavLink>
        <NavLink to="/compare" end className={navClass}>
          Compare
        </NavLink>
      </nav>
      <div className="border-t border-border p-3">
        <a
          href={GITHUB_REPO_URL}
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Open project on GitHub in a new tab"
          className={cn(
            'group flex w-full items-center gap-3 rounded-lg border border-border bg-background p-3 shadow-sm',
            'transition-all hover:border-primary/50 hover:bg-accent/80 hover:shadow-md',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
          )}
        >
          <span
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-muted text-foreground ring-1 ring-border transition-colors group-hover:bg-primary/10 group-hover:text-primary"
            aria-hidden
          >
            <Github className="h-5 w-5" strokeWidth={2} />
          </span>
          <span className="min-w-0 flex-1 text-left">
            <span className="block text-sm font-semibold leading-tight text-foreground">GitHub</span>
            <span className="mt-0.5 block text-xs text-muted-foreground">View source code</span>
          </span>
          <ExternalLink
            className="h-4 w-4 shrink-0 text-muted-foreground transition-colors group-hover:text-primary"
            aria-hidden
          />
        </a>
      </div>
    </aside>
  );
}
