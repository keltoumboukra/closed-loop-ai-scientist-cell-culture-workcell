import { useMemo } from 'react';
import Plot from './Plot';
import { MetricDefinitionButton } from './MetricDefinitionButton';
import { iterationIdFromLegendClick } from '@/lib/chartIterationLegend';
import { jitter01 } from '@/lib/hashJitter';
import { colorForIterationId, hexToRgba } from '@/lib/iterationColors';
import { bestWellForMetric, getMetricNumericValue } from '@/lib/metrics';
import { formatDesignParamsPlotlyHtml } from '@/lib/wellDesign';
import { METRIC_LABELS } from '@/types';
import type { IterationMetrics, MetricKey } from '@/types';

type Props = {
  metric: MetricKey;
  /** Same order as iteration order on the x-axis (e.g. sorted by id). */
  iterations: IterationMetrics[];
  onIterationLegendClick?: (iterationId: string) => void;
};

function paddedYRange(values: number[]): [number, number] {
  if (values.length === 0) return [0, 1];
  const yMin = Math.min(...values);
  const yMax = Math.max(...values);
  const span = yMax - yMin || Math.abs(yMax) * 0.05 || 0.1;
  const mag = Math.max(Math.abs(yMin), Math.abs(yMax), 1e-6);
  const topPad = span * 0.3 + Math.max(mag * 0.02, 0.012);
  const bottomPad = span * 0.18 + Math.max(mag * 0.012, 0.008);
  return [yMin - bottomPad, yMax + topPad];
}

/**
 * One violin + jittered wells per iteration; colors match Overview (iteration palette).
 */
export function MetricViolinDistribution({ metric, iterations, onIterationLegendClick }: Props) {
  const chart = useMemo(() => {
    const categoryOrder = iterations.map((i) => i.iteration_id);
    const catIndex = new Map(categoryOrder.map((id, i) => [id, i]));
    const jitterScale = Math.min(0.32, 0.9 / Math.max(8, categoryOrder.length));

    const traces: object[] = [];
    const allY: number[] = [];
    let omittedNullDoubling = 0;

    for (const it of iterations) {
      const id = it.iteration_id;
      const ix = catIndex.get(id) ?? 0;
      const color = colorForIterationId(id, categoryOrder);

      const xsV: number[] = [];
      const ysV: number[] = [];
      const wells: string[] = [];
      const designHtml: string[] = [];

      for (const r of it.results) {
        const v = getMetricNumericValue(r, metric);
        if (v === null) {
          if (metric === 'doubling_time_hours') omittedNullDoubling += 1;
          continue;
        }
        xsV.push(ix);
        ysV.push(v);
        wells.push(r.well);
        designHtml.push(formatDesignParamsPlotlyHtml(r.params));
        allY.push(v);
      }

      if (xsV.length === 0) continue;

      traces.push({
        type: 'violin' as const,
        x: xsV,
        y: ysV,
        name: id,
        fillcolor: hexToRgba(color, 0.38),
        line: { color, width: 1 },
        box: { visible: false },
        meanline: { visible: false },
        points: false,
        width: 0.72,
        side: 'both' as const,
        hoverinfo: 'skip' as const,
        cliponaxis: false,
        showlegend: true,
      });

      const xJittered = xsV.map((_, i) => ix + jitter01(wells[i]!, id) * jitterScale);

      traces.push({
        type: 'scatter' as const,
        x: xJittered,
        y: ysV,
        text: wells,
        customdata: designHtml,
        mode: 'markers' as const,
        legendgroup: id,
        marker: {
          color,
          size: 6,
          opacity: 0.7,
          line: { width: 0 },
        },
        showlegend: false,
        hovertemplate: `<b>${id}</b><br>%{text}<br>%{y:.4f}<br>%{customdata}<extra></extra>`,
      });
    }

    const bestX: number[] = [];
    const bestY: number[] = [];
    const bestText: string[] = [];
    const bestColors: string[] = [];
    const bestDesignHtml: string[] = [];

    for (const it of iterations) {
      const best = bestWellForMetric(it.results, metric);
      if (!best) continue;
      const id = it.iteration_id;
      const row = it.results.find((r) => r.well === best.well);
      bestX.push(catIndex.get(id) ?? 0);
      bestY.push(best.value);
      bestText.push(best.well);
      bestDesignHtml.push(formatDesignParamsPlotlyHtml(row?.params ?? {}));
      bestColors.push(colorForIterationId(id, categoryOrder));
      allY.push(best.value);
    }

    if (bestX.length > 0) {
      traces.push({
        type: 'scatter' as const,
        mode: 'markers+text' as const,
        name: 'Best per iteration',
        x: bestX,
        y: bestY,
        text: bestText,
        customdata: bestDesignHtml,
        textposition: 'top center' as const,
        textfont: { size: 11, color: '#0f172a' },
        marker: {
          color: bestColors,
          size: 12,
          symbol: 'diamond',
          line: { width: 1.5, color: '#0f172a' },
          opacity: 1,
        },
        cliponaxis: false,
        hovertemplate: '<b>Best %{text}</b><br>%{y:.4f}<br>%{customdata}<extra></extra>',
        showlegend: true,
      });
    }

    const yRange = paddedYRange(allY);

    const emptyNote =
      metric === 'doubling_time_hours' && omittedNullDoubling > 0
        ? `${omittedNullDoubling} well readings omitted (no valid doubling time).`
        : null;

    const nCats = categoryOrder.length;
    const tickvals = categoryOrder.map((_, i) => i);
    const yTitle = METRIC_LABELS[metric];

    /** Stable identity for react-plotly; avoids Plotly.react on every parent render (see debug H1). */
    const layout = {
      uirevision: `violin-${metric}`,
      xaxis: {
        title: { text: 'Iteration' },
        type: 'linear' as const,
        tickmode: 'array' as const,
        tickvals,
        ticktext: categoryOrder,
        range: [-0.55, Math.max(nCats - 1, 0) + 0.55] as [number, number],
        zeroline: false,
        gridcolor: '#e5e7eb',
      },
      yaxis: {
        title: { text: yTitle },
        gridcolor: '#e5e7eb',
        range: yRange,
        fixedrange: false,
      },
      margin: { l: 58, r: 12, t: 72, b: 64 },
      height: 300,
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: { size: 11 },
      showlegend: true,
      legend: {
        orientation: 'h' as const,
        y: 1.02,
        yanchor: 'bottom' as const,
        x: 0,
        xanchor: 'left' as const,
        font: { size: 11 },
      },
      hovermode: 'closest' as const,
      hoverlabel: { namelength: -1, align: 'left' as const },
    };

    const config = { displayModeBar: false, responsive: true };

    return {
      traces,
      categoryOrder,
      yTitle,
      emptyNote,
      yRange,
      nCats,
      hasData: traces.length > 0,
      layout,
      config,
    };
  }, [metric, iterations]);

  const validIterationIds = iterations.map((i) => i.iteration_id);

  const handleLegendClick = (e: Readonly<{ curveNumber: number }>) => {
    if (!onIterationLegendClick) return true;
    const id = iterationIdFromLegendClick(chart.traces, e.curveNumber, validIterationIds);
    if (!id) return false;
    onIterationLegendClick(id);
    return false;
  };

  if (!chart.hasData) {
    return (
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">{METRIC_LABELS[metric]}</span>
          <MetricDefinitionButton metric={metric} />
        </div>
        <p className="text-sm text-muted-foreground">
          {metric === 'doubling_time_hours'
            ? 'No wells with a valid doubling time in these iterations.'
            : 'No numeric data to plot for this metric.'}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium">{METRIC_LABELS[metric]}</span>
        <MetricDefinitionButton metric={metric} />
      </div>
      {chart.emptyNote ? (
        <p className="text-xs text-muted-foreground">{chart.emptyNote}</p>
      ) : null}
      <div className="relative w-full mb-2">
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
