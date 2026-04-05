import { useState, useMemo, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { PlateHeatmap } from '@/components/plate/PlateHeatmap';
import { WellDetailPanel } from '@/components/plate/WellDetailPanel';
import { MetricDefinitionButton } from '@/components/charts/MetricDefinitionButton';
import { PageHeader } from '@/components/layout/PageHeader';
import { WellDesignInline, WellIdWithDesign } from '@/components/wells/WellIdWithDesign';
import { useIteration, useIterations } from '@/api/client';
import { sortIterationIds } from '@/lib/sortIterationIds';
import { ApiErrorState } from '@/components/feedback/ApiErrorState';
import { EmptyState } from '@/components/feedback/EmptyState';
import { bestWellForMetric, meanMetricValue } from '@/lib/metrics';
import type { MetricKey } from '@/types';
import { METRIC_LABELS } from '@/types';

export function IterationView() {
  const { iterationId } = useParams<{ iterationId: string }>();
  const navigate = useNavigate();
  const { data: iterationSummaries } = useIterations();
  const { data: iteration, isLoading, error, refetch } = useIteration(iterationId ?? '');
  const [selectedWell, setSelectedWell] = useState<string | null>(null);
  const [metric, setMetric] = useState<MetricKey>('growth_rate');

  const iterationOptions = useMemo(() => {
    const ids = [...(iterationSummaries?.map((s) => s.iteration_id) ?? [])];
    if (iterationId && !ids.includes(iterationId)) {
      ids.push(iterationId);
    }
    return sortIterationIds(ids);
  }, [iterationSummaries, iterationId]);

  useEffect(() => {
    setSelectedWell(null);
  }, [iterationId]);

  const onIterationChange = (id: string | null) => {
    if (!id) return;
    setSelectedWell(null);
    void navigate(`/iterations/${encodeURIComponent(id)}`);
  };

  const selectedWellData = useMemo(() => {
    if (!selectedWell || !iteration) return null;
    return iteration.results.find((r) => r.well === selectedWell) ?? null;
  }, [selectedWell, iteration]);

  const bestForMetric = useMemo(() => {
    if (!iteration) return null;
    return bestWellForMetric(iteration.results, metric);
  }, [iteration, metric]);

  const meanForMetric = useMemo(() => {
    if (!iteration) return null;
    return meanMetricValue(iteration.results, metric);
  }, [iteration, metric]);

  const bestWellRow = useMemo(() => {
    if (!bestForMetric || !iteration) return null;
    return iteration.results.find((r) => r.well === bestForMetric.well) ?? null;
  }, [bestForMetric, iteration]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-full max-w-xl" />
        <Skeleton className="h-40 w-full rounded-xl" />
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

  if (!iteration) {
    return (
      <div className="space-y-6">
        <EmptyState
          title="Iteration"
          description="No data found for this iteration. Check the URL or ensure the parser has run."
          mascot="iteration"
        />
        {iterationOptions.length > 0 ? (
          <div className="flex max-w-md flex-col gap-2">
            <span className="text-sm font-medium text-foreground">Open another iteration</span>
            <Select onValueChange={(id: string | null) => onIterationChange(id)}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select iteration" />
              </SelectTrigger>
              <SelectContent>
                {iterationOptions.map((id: string) => (
                  <SelectItem key={id} value={id}>
                    {id}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        ) : null}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Iteration"
        description="Inspect one run's 96-well plate. Choose a metric to color wells, click a well for details, or switch runs from the menu."
        mascot="iteration"
        titleAddon={
          iterationOptions.length > 0 ? (
            <div className="flex flex-wrap items-center gap-2">
              <label htmlFor="iteration-view-select" className="sr-only">
                Choose iteration
              </label>
              <Select
                value={iteration.iteration_id}
                onValueChange={(id: string | null) => onIterationChange(id)}
              >
                <SelectTrigger id="iteration-view-select" className="w-[min(100%,22rem)] h-10 text-base">
                  <SelectValue placeholder="Select iteration" />
                </SelectTrigger>
                <SelectContent>
                  {iterationOptions.map((id: string) => (
                    <SelectItem key={id} value={id}>
                      {id}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          ) : (
            <p className="text-lg font-medium text-foreground tabular-nums">{iteration.iteration_id}</p>
          )
        }
      />

      {/* Summary stats (follow selected metric) */}
      <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
        <span className="text-muted-foreground">
          Wells: <span className="text-foreground font-medium">{iteration.results.length}</span>
        </span>
        <span className="text-muted-foreground">
          Best ({METRIC_LABELS[metric]}):{' '}
          <span className="text-foreground font-medium inline-flex flex-wrap items-baseline gap-x-1.5 gap-y-1">
            {bestForMetric ? (
              <>
                <span className="inline-flex flex-wrap items-baseline gap-x-1">
                  well{' '}
                  <WellIdWithDesign
                    wellId={bestForMetric.well}
                    params={bestWellRow?.params}
                    lazyLoadIterationId={iteration.iteration_id}
                  />
                  <span className="tabular-nums">({bestForMetric.value.toFixed(4)})</span>
                </span>
                {bestWellRow ? <WellDesignInline params={bestWellRow.params} /> : null}
              </>
            ) : (
              '—'
            )}
          </span>
        </span>
        <span className="text-muted-foreground">
          Mean ({METRIC_LABELS[metric]}):{' '}
          <span className="text-foreground font-medium">
            {meanForMetric != null ? meanForMetric.toFixed(4) : '—'}
          </span>
        </span>
      </div>

      {/* Plate + well detail: controls sit directly above the heatmap */}
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start">
        <Card className="min-w-0 flex-1">
          <CardHeader className="space-y-3 border-b border-border/60 pb-4">
            <div>
              <CardTitle className="text-base">Well plate</CardTitle>
              <CardDescription>
                Choose which metric sets the blue scale. Darker wells are better for that metric
                (see legend below the grid).
              </CardDescription>
            </div>
            <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center">
              <span className="text-sm font-medium text-foreground">Color by</span>
              <div className="flex flex-wrap items-center gap-2">
                <Select
                  value={metric}
                  onValueChange={(v) => {
                    if (v) setMetric(v as MetricKey);
                  }}
                >
                  <SelectTrigger className="w-[min(100%,18rem)]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {(Object.keys(METRIC_LABELS) as MetricKey[]).map((key) => (
                      <SelectItem key={key} value={key}>
                        {METRIC_LABELS[key]}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <MetricDefinitionButton metric={metric} />
              </div>
            </div>
          </CardHeader>
          <CardContent className="pt-4">
            <PlateHeatmap
              results={iteration.results}
              metric={metric}
              selectedWell={selectedWell}
              onSelectWell={setSelectedWell}
            />
          </CardContent>
        </Card>

        {selectedWellData && (
          <WellDetailPanel
            well={selectedWellData}
            iterationId={iteration.iteration_id}
            onClose={() => setSelectedWell(null)}
          />
        )}
      </div>
    </div>
  );
}
