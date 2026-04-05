import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LoopyMascot } from '@/components/mascot/LoopyMascot';

type Props = {
  title?: string;
  message: string;
  onRetry?: () => void;
};

/** Consistent card for TanStack Query / fetch failures. */
export function ApiErrorState({ title = 'Could not load data', message, onRetry }: Props) {
  return (
    <div className="flex max-w-xl items-start gap-3 sm:gap-4">
      <div className="shrink-0 pt-1 select-none pointer-events-none" aria-hidden>
        <LoopyMascot variant="error" maxHeightClass="max-h-14 sm:max-h-16" className="opacity-90" />
      </div>
      <Card className="min-w-0 flex-1 border-destructive/50">
        <CardHeader>
          <CardTitle className="text-destructive text-base">{title}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground break-words">{message}</p>
          {onRetry ? (
            <Button type="button" variant="outline" size="sm" onClick={onRetry}>
              Try again
            </Button>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}
