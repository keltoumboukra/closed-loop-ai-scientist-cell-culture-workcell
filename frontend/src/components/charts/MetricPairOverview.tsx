import { useMemo } from 'react';
import Plot from './Plot';
import { MetricPairDefinitionButton } from './MetricPairDefinitionButton';
import { iterationIdFromLegendClick } from '@/lib/chartIterationLegend';
import { bestWellForMetric, getMetricNumericValue } from '@/lib/metrics';
import { colorForIterationId } from '@/lib/iterationColors';
import { formatDesignParamsPlotlyHtml } from '@/lib/wellDesign';
import { METRIC_LABELS } from '@/types';
import type { IterationMetrics, MetricKey } from '@/types';

type Props = {
  iterations: IterationMetrics[];
  xMetric: MetricKey;
  yMetric: MetricKey;
  onIterationLegendClick?: (iterationId: string) => void;
};

function paddedRange(values: number[]): [number, number] {
  if (values.length === 0) return [0, 1];
  const vmin = Math.min(...values);
  const vmax = Math.max(...values);
  const span = vmax - vmin || Math.abs(vmax) * 0.05 || 0.1;
  const mag = Math.max(Math.abs(vmin), Math.abs(vmax), 1e-6);
  const pad = span * 0.12 + Math.max(mag * 0.02, 0.012);
  return [vmin - pad, vmax + pad];
}

/**
 * One 2D scatter: x and y are real metrics per well; color = iteration; diamonds = best on **y** per iteration.
 */
export function MetricPairOverview({ iterations, xMetric, yMetric, onIterationLegendClick }: Props) {
  const chart = useMemo(() => {
    const categoryOrder = iterations.map((i) => i.iteration_id);
    const traces: object[] = [];
    const allX: number[] = [];
    const allY: number[] = [];
    let iterationTraceCount = 0;

    for (const it of iterations) {
      const id = it.iteration_id;
      const color = colorForIterationId(id, categoryOrder);
      const xList: number[] = [];
      const yList: number[] = [];
      const labels: string[] = [];
      const designHtml: string[] = [];

      for (const r of it.results) {
        const xv = getMetricNumericValue(r, xMetric);
        const yv = getMetricNumericValue(r, yMetric);
        if (xv === null || yv === null) continue;
        xList.push(xv);
        yList.push(yv);
        labels.push(r.well);
        designHtml.push(formatDesignParamsPlotlyHtml(r.params));
        allX.push(xv);
        allY.push(yv);
      }

      if (xList.length === 0) continue;

      iterationTraceCount += 1;
      traces.push({
        type: 'scatter' as const,
        mode: 'markers' as const,
        name: id,
        x: xList,
        y: yList,
        text: labels,
        customdata: designHtml,
        legendgroup: id,
        marker: {
          color,
          size: 7,
          opacity: 0.72,
          line: { width: 0 },
        },
        hovertemplate:
          `<b>${id}</b><br>Well %{text}<br>` +
          `${METRIC_LABELS[xMetric]}: %{x:.4f}<br>${METRIC_LABELS[yMetric]}: %{y:.4f}<br>%{customdata}<extra></extra>`,
      });
    }

    const bestX: number[] = [];
    const bestY: number[] = [];
    const bestText: string[] = [];
    const bestColors: string[] = [];
    const bestDesignHtml: string[] = [];

    for (const it of iterations) {
      const best = bestWellForMetric(it.results, yMetric);
      if (!best) continue;
      const row = it.results.find((r) => r.well === best.well);
      if (!row) continue;
      const xv = getMetricNumericValue(row, xMetric);
      const yv = getMetricNumericValue(row, yMetric);
      if (xv === null || yv === null) continue;
      bestX.push(xv);
      bestY.push(yv);
      bestText.push(best.well);
      bestDesignHtml.push(formatDesignParamsPlotlyHtml(row.params));
      bestColors.push(colorForIterationId(it.iteration_id, categoryOrder));
      allX.push(xv);
      allY.push(yv);
    }

    if (bestX.length > 0) {
      traces.push({
        type: 'scatter' as const,
        mode: 'markers+text' as const,
        name: 'Best per iteration (by Y)',
        x: bestX,
        y: bestY,
        text: bestText,
        customdata: bestDesignHtml,
        textposition: 'top center' as const,
        textfont: { size: 10, color: '#0f172a' },
        legendgroup: 'best',
        marker: {
          color: bestColors,
          size: 13,
          symbol: 'diamond',
          line: { width: 1.5, color: '#0f172a' },
          opacity: 1,
        },
        cliponaxis: false,
        hovertemplate:
          '<b>Best %{text}</b><br>' +
          `${METRIC_LABELS[xMetric]}: %{x:.4f}<br>${METRIC_LABELS[yMetric]}: %{y:.4f}<br>%{customdata}<extra></extra>`,
      });
    }

    const xRange = allX.length ? paddedRange(allX) : ([0, 1] as [number, number]);
    const yRange = allY.length ? paddedRange(allY) : ([0, 1] as [number, number]);

    const xTitle = METRIC_LABELS[xMetric];
    const yTitle = METRIC_LABELS[yMetric];

    const layout = {
      uirevision: `pair-${xMetric}-${yMetric}`,
      xaxis: {
        title: { text: xTitle },
        gridcolor: '#e5e7eb',
        range: xRange,
        zeroline: false,
        fixedrange: false,
      },
      yaxis: {
        title: { text: yTitle },
        gridcolor: '#e5e7eb',
        range: yRange,
        zeroline: false,
        fixedrange: false,
      },
      margin: { l: 58, r: 12, t: 52, b: 56 },
      height: 420,
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: { size: 11 },
      showlegend: true,
      // Keep legend inside the figure (paper y >= 0). A bottom legend (y negative) sits in the
      // margin and is easy to clip when Card uses overflow-hidden or when the hover layer draws.
      legend: {
        orientation: 'h' as const,
        y: 1.02,
        yanchor: 'bottom' as const,
        x: 0,
        xanchor: 'left' as const,
        font: { size: 10 },
      },
      hovermode: 'closest' as const,
      hoverlabel: { namelength: -1, align: 'left' as const },
    };

    const config = { displayModeBar: false, responsive: true };

    return {
      traces,
      xTitle,
      yTitle,
      xRange,
      yRange,
      hasWellPoints: iterationTraceCount > 0,
      layout,
      config,
    };
  }, [iterations, xMetric, yMetric]);

  const validIterationIds = iterations.map((i) => i.iteration_id);

  const handleLegendClick = (e: Readonly<{ curveNumber: number }>) => {
    if (!onIterationLegendClick) return true;
    const id = iterationIdFromLegendClick(chart.traces, e.curveNumber, validIterationIds);
    if (!id) return false;
    onIterationLegendClick(id);
    return false;
  };

  if (!chart.hasWellPoints) {
    return (
      <div className="rounded-md border border-dashed p-6 text-center text-sm text-muted-foreground">
        No wells with valid values for both selected metrics (e.g. missing doubling time). Try
        different axes.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="flex gap-2.5 items-start">
        <h3 className="min-w-0 flex-1 text-base font-semibold leading-snug tracking-tight text-foreground">
          {chart.yTitle}{' '}
          <span className="font-normal text-muted-foreground">vs</span> {chart.xTitle}
        </h3>
        <MetricPairDefinitionButton xMetric={xMetric} yMetric={yMetric} />
      </div>
      <div className="relative w-full pb-1">
        <Plot
          data={chart.traces}
          layout={chart.layout}
          config={chart.config}
          useResizeHandler
          style={{ width: '100%' }}
          onLegendClick={onIterationLegendClick ? handleLegendClick : undefined}
        />
      </div>
    </div>
  );
}
