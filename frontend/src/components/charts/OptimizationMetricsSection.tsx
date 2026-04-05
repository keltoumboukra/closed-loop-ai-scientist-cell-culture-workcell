import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { IterationNavChips } from './IterationNavChips';
import { MetricViolinDistribution } from './MetricViolinDistribution';
import { DASHBOARD_METRICS } from '@/lib/metricDefinitions';
import type { IterationMetrics, MetricKey } from '@/types';

type Props = {
  iterations: IterationMetrics[];
  onIterationLegendClick?: (iterationId: string) => void;
};

/** Distributions per iteration (violins) for each metric. */
export function OptimizationMetricsSection({ iterations, onIterationLegendClick }: Props) {
  return (
    <Card className="overflow-visible">
      <CardHeader>
        <CardTitle className="text-sm">Detailed view: distribution per iteration</CardTitle>
        <p className="text-xs text-muted-foreground font-normal leading-relaxed">
          One violin per iteration with all wells shown as points. Iteration colors match the Overview
          tab. Diamonds mark the best well per iteration (highest growth rate, max OD, and R²; lowest
          doubling time). Click an iteration in the legend under a chart to add or remove it from
          the dashboard filter. Use <span className="font-medium text-foreground">Open iteration</span>{' '}
          below to open an iteration page.
        </p>
      </CardHeader>
      <CardContent className="space-y-10">
        {DASHBOARD_METRICS.map((metric: MetricKey) => (
          <MetricViolinDistribution
            key={metric}
            metric={metric}
            iterations={iterations}
            onIterationLegendClick={onIterationLegendClick}
          />
        ))}
        <IterationNavChips iterationIds={iterations.map((i) => i.iteration_id)} />
      </CardContent>
    </Card>
  );
}
