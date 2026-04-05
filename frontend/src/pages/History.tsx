import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { PageHeader } from '@/components/layout/PageHeader';
import { WellIdWithDesign } from '@/components/wells/WellIdWithDesign';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';
import { useIterations } from '@/api/client';
import { ApiErrorState } from '@/components/feedback/ApiErrorState';
import { EmptyState } from '@/components/feedback/EmptyState';
import type { IterationSummary } from '@/types';

type SortKey = keyof IterationSummary;
type SortDir = 'asc' | 'desc';

const COLUMNS: { key: SortKey; label: string }[] = [
  { key: 'iteration_id', label: 'Iteration' },
  { key: 'well_count', label: 'Wells' },
  { key: 'mean_growth_rate', label: 'Mean Growth Rate' },
  { key: 'best_growth_rate', label: 'Best Growth Rate' },
  { key: 'best_well', label: 'Best Well' },
];

export function History() {
  const { data: iterations, isLoading, error, refetch } = useIterations();
  const [sortKey, setSortKey] = useState<SortKey>('iteration_id');
  const [sortDir, setSortDir] = useState<SortDir>('desc');

  const sorted = useMemo(() => {
    if (!iterations) return [];
    return [...iterations].sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      const cmp = typeof av === 'string' ? av.localeCompare(bv as string) : (av as number) - (bv as number);
      return sortDir === 'asc' ? cmp : -cmp;
    });
  }, [iterations, sortKey, sortDir]);

  const handleSort = (key: SortKey) => {
    if (key === sortKey) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-[200px] w-full max-w-4xl" />
      </div>
    );
  }

  if (error) {
    return (
      <ApiErrorState
        message={(error as Error).message}
        onRetry={() => {
          void refetch();
        }}
      />
    );
  }

  if (!iterations || iterations.length === 0) {
    return (
      <EmptyState
        title="History"
        description="No iterations found. Generate mock data or run an experiment."
        mascot="history"
      />
    );
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="History"
        description="Browse every run with a short summary. Sort columns by clicking headers, then open an iteration to see the full plate."
        mascot="history"
      />

      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              {COLUMNS.map((col) => (
                <TableHead
                  key={col.key}
                  className="cursor-pointer select-none hover:bg-muted/50 transition-colors"
                  onClick={() => handleSort(col.key)}
                >
                  <span className="flex items-center gap-1">
                    {col.label}
                    {sortKey === col.key && (
                      <span className="text-xs">{sortDir === 'asc' ? ' ^' : ' v'}</span>
                    )}
                  </span>
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {sorted.map((it) => (
              <TableRow key={it.iteration_id} className="hover:bg-muted/30">
                <TableCell>
                  <Link
                    to={`/iterations/${it.iteration_id}`}
                    className="text-primary hover:underline font-medium"
                  >
                    {it.iteration_id}
                  </Link>
                </TableCell>
                <TableCell>{it.well_count}</TableCell>
                <TableCell className="font-mono">{it.mean_growth_rate.toFixed(4)}</TableCell>
                <TableCell className="font-mono">{it.best_growth_rate.toFixed(4)}</TableCell>
                <TableCell>
                  <WellIdWithDesign wellId={it.best_well} lazyLoadIterationId={it.iteration_id} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
