import { Link, useLocation } from 'react-router-dom';
import { Button, buttonVariants } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export type OopsLocationState = {
  message?: string;
};

/**
 * Full-page recovery UI after a render error (navigated here by ErrorBoundary).
 */
export function Oops() {
  const location = useLocation();
  const state = (location.state ?? undefined) as OopsLocationState | undefined;
  const message = state?.message;

  return (
    <div className="mx-auto flex max-w-lg flex-col items-center gap-6 py-4 text-center">
      <p className="text-sm text-muted-foreground leading-relaxed">
        An unexpected problem occurred in the UI. Try reloading the page or return to the dashboard.
        The sidebar still works if you prefer to navigate away.
      </p>
      {message ? (
        <details className="w-full text-left text-xs text-muted-foreground">
          <summary className="cursor-pointer select-none text-sm font-medium text-foreground">
            Technical detail
          </summary>
          <pre className="mt-2 max-h-40 overflow-auto whitespace-pre-wrap break-words rounded-md border border-border bg-muted/50 p-3">
            {message}
          </pre>
        </details>
      ) : null}
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
