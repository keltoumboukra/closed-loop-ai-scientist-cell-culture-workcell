import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PageHeader } from '@/components/layout/PageHeader';
import { DashboardIterationFilter } from '@/components/dashboard/DashboardIterationFilter';
import { sortIterationIds } from '@/lib/sortIterationIds';
import { WellIdWithDesign } from '@/components/wells/WellIdWithDesign';
import { OverviewMetricsSection } from '@/components/charts/OverviewMetricsSection';
import { OptimizationMetricsSection } from '@/components/charts/OptimizationMetricsSection';
import { useIterations, useIterationsBatch } from '@/api/client';
import { ApiErrorState } from '@/components/feedback/ApiErrorState';
import { EmptyState } from '@/components/feedback/EmptyState';
import type { IterationMetrics } from '@/types';

export function Dashboard() {
  const queryClient = useQueryClient();
  const { data: summaries, isLoading: listLoading, error: listError, refetch: refetchList } =
    useIterations();

  const allIds = useMemo(() => summaries?.map((s) => s.iteration_id) ?? [], [summaries]);

  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const prevAllIdsRef = useRef<string[]>([]);
  const selectionInitializedRef = useRef(false);

  useEffect(() => {
    if (allIds.length === 0) return;
    const sorted = sortIterationIds(allIds);
    const prevList = prevAllIdsRef.current;
    const prevSet = new Set(prevList);

    setSelectedIds((prevSel) => {
      if (!selectionInitializedRef.current) {
        selectionInitializedRef.current = true;
        return new Set(sorted);
      }
      const next = new Set<string>();
      for (const id of sorted) {
        if (!prevSet.has(id)) next.add(id);
        else if (prevSel.has(id)) next.add(id);
      }
      return next;
    });
    prevAllIdsRef.current = sorted;
  }, [allIds]);

  const iterationIds = allIds;
  const batch = useIterationsBatch(iterationIds);

  const metricsOrdered = useMemo((): IterationMetrics[] => {
    if (!summaries?.length) return [];
    const out: IterationMetrics[] = [];
    for (const s of summaries) {
      const hit = batch.find((q) => q.data?.iteration_id === s.iteration_id);
      if (!hit?.data) return [];
      out.push(hit.data);
    }
    return out;
  }, [summaries, batch]);

  const filteredSummaries = useMemo(
    () => summaries?.filter((s) => selectedIds.has(s.iteration_id)) ?? [],
    [summaries, selectedIds],
  );

  const filteredMetrics = useMemo(
    () => metricsOrdered.filter((m) => selectedIds.has(m.iteration_id)),
    [metricsOrdered, selectedIds],
  );

  const sortedFilteredIds = useMemo(
    () => sortIterationIds(filteredSummaries.map((s) => s.iteration_id)),
    [filteredSummaries],
  );

  const globalBestParams = useMemo(() => {
    if (filteredSummaries.length === 0) return null;
    const gb = filteredSummaries.reduce((best, it) =>
      it.best_growth_rate > best.best_growth_rate ? it : best,
    );
    const it = filteredMetrics.find((m) => m.iteration_id === gb.iteration_id);
    return it?.results.find((r) => r.well === gb.best_well)?.params ?? null;
  }, [filteredSummaries, filteredMetrics]);

  const latestBestParams = useMemo(() => {
    if (filteredSummaries.length === 0 || sortedFilteredIds.length === 0) return null;
    const latestId = sortedFilteredIds[sortedFilteredIds.length - 1];
    const latest = filteredSummaries.find((s) => s.iteration_id === latestId);
    if (!latest) return null;
    const it = filteredMetrics.find((m) => m.iteration_id === latest.iteration_id);
    return it?.results.find((r) => r.well === latest.best_well)?.params ?? null;
  }, [filteredSummaries, sortedFilteredIds, filteredMetrics]);

  const detailLoading = summaries != null && summaries.length > 0 && batch.some((q) => q.isLoading);
  const detailError = batch.find((q) => q.error)?.error;

  const retryCharts = () => {
    void refetchList();
    void queryClient.invalidateQueries({ queryKey: ['iteration'] });
  };

  /** Legend clicks on charts toggle iteration visibility (same as the filter checkboxes). */
  const toggleIterationInFilter = useCallback((iterationId: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(iterationId)) next.delete(iterationId);
      else next.add(iterationId);
      return next;
    });
  }, []);

  if (listLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-48 w-full max-w-3xl" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Skeleton className="h-28" />
          <Skeleton className="h-28" />
          <Skeleton className="h-28" />
        </div>
        <Skeleton className="min-h-[1200px] w-full" />
      </div>
    );
  }

  if (listError) {
    return (
      <ApiErrorState
        message={(listError as Error).message}
        onRetry={() => {
          void refetchList();
        }}
      />
    );
  }

  if (!summaries || summaries.length === 0) {
    return (
      <EmptyState
        title="Dashboard"
        description="No iterations found. Run an experiment or generate mock data to get started."
        mascot="dashboard"
      />
    );
  }

  const totalIterations = filteredSummaries.length;
  const globalBest =
    filteredSummaries.length > 0
      ? filteredSummaries.reduce((best, it) =>
          it.best_growth_rate > best.best_growth_rate ? it : best,
        )
      : null;
  const latestId = sortedFilteredIds[sortedFilteredIds.length - 1];
  const latest = latestId ? filteredSummaries.find((s) => s.iteration_id === latestId) : undefined;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        description="See how your experiment runs compare across iterations. Pick which runs to include, review the summary cards, then explore Overview and Detailed charts. The legend and filters here stay in sync."
        mascot="dashboard"
      />

      <DashboardIterationFilter
        iterationIds={allIds}
        selectedIds={selectedIds}
        onSelectedIdsChange={setSelectedIds}
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground font-normal">
              Iterations shown
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{totalIterations}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground font-normal">Best Growth Rate</CardTitle>
          </CardHeader>
          <CardContent>
            {globalBest ? (
              <>
                <p className="text-3xl font-bold">
                  {globalBest.best_growth_rate.toFixed(4)}{' '}
                  <span className="text-base font-normal text-muted-foreground">/h</span>
                </p>
                <p className="text-sm text-muted-foreground mt-1 flex flex-wrap items-baseline gap-x-2 gap-y-1">
                  <span>
                    Well{' '}
                    <WellIdWithDesign
                      wellId={globalBest.best_well}
                      params={globalBestParams ?? undefined}
                      lazyLoadIterationId={globalBest.iteration_id}
                    />{' '}
                    in {globalBest.iteration_id}
                  </span>
                </p>
              </>
            ) : (
              <p className="text-sm text-muted-foreground">No iterations selected</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground font-normal">Latest (in selection)</CardTitle>
          </CardHeader>
          <CardContent>
            {latest ? (
              <>
                <Link
                  to={`/iterations/${latest.iteration_id}`}
                  className="text-3xl font-bold text-primary hover:underline"
                >
                  {latest.iteration_id}
                </Link>
                <p className="text-sm text-muted-foreground mt-1">
                  <span className="inline-flex flex-wrap items-baseline gap-x-1">
                    {latest.well_count} wells, best: {latest.best_growth_rate.toFixed(4)} /h (
                    <WellIdWithDesign
                      wellId={latest.best_well}
                      params={latestBestParams ?? undefined}
                      lazyLoadIterationId={latest.iteration_id}
                      showAffordance={false}
                      className="text-foreground"
                    />
                    )
                  </span>
                </p>
              </>
            ) : (
              <p className="text-sm text-muted-foreground">No iterations selected</p>
            )}
          </CardContent>
        </Card>
      </div>

      {detailError ? (
        <ApiErrorState
          title="Could not load iteration details for charts"
          message={(detailError as Error).message}
          onRetry={retryCharts}
        />
      ) : detailLoading ? (
        <div className="space-y-4">
          <Skeleton className="h-10 w-full max-w-md" />
          <Skeleton className="min-h-[1100px] w-full" />
        </div>
      ) : metricsOrdered.length === summaries.length ? (
        selectedIds.size === 0 ? (
          <div className="rounded-md border border-dashed p-8 text-center text-sm text-muted-foreground">
            Select at least one iteration above to view charts.
          </div>
        ) : (
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="mb-4 h-9 w-fit max-w-full">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="detailed">Detailed</TabsTrigger>
            </TabsList>
            <TabsContent value="overview" className="mt-0">
              <OverviewMetricsSection
                iterations={filteredMetrics}
                onIterationLegendClick={toggleIterationInFilter}
              />
            </TabsContent>
            <TabsContent value="detailed" className="mt-0">
              <OptimizationMetricsSection
                iterations={filteredMetrics}
                onIterationLegendClick={toggleIterationInFilter}
              />
            </TabsContent>
          </Tabs>
        )
      ) : (
        <ApiErrorState
          title="Incomplete iteration data"
          message="Some iterations could not be loaded."
          onRetry={retryCharts}
        />
      )}
    </div>
  );
}
