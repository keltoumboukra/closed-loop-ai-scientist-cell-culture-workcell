/**
 * Display helpers for `params` on each well (from `well_to_design_mapping` via parser / API).
 *
 * Order follows `Object.keys(params)`, which matches key order in the iteration JSON when the
 * client parses API responses (same as typical `well_to_design_mapping.json` on disk).
 */

/** Turn a snake_case API key into a short title (no fixed list of experiment keys). */
function keyToLabel(key: string): string {
  return key
    .split('_')
    .map((seg) => {
      if (seg === 'mM') return 'mM';
      if (seg === 'uL' || seg === 'μL') return 'µL';
      const lower = seg.toLowerCase();
      if (lower === 'mm') return 'mm';
      if (lower === 'per') return 'per';
      if (seg === 'L') return 'L';
      if (seg === 'g') return 'g';
      if (seg.length <= 4 && seg === seg.toUpperCase()) return seg;
      return seg.charAt(0).toUpperCase() + seg.slice(1).toLowerCase();
    })
    .join(' ');
}

function formatDesignType(v: number): string {
  if (Math.abs(v - 0) < 1e-6) return 'LHS';
  if (Math.abs(v - 1) < 1e-6) return 'Media blank';
  if (Math.abs(v - 2) < 1e-6) return 'Base control';
  return String(v);
}

function formatParamValue(key: string, v: number): string {
  if (!Number.isFinite(v)) return String(v);
  if (key === 'design_type') return formatDesignType(v);

  const decimals =
    key.includes('_g_per_L') || key.includes('_mM') || key.includes('_mm') ? 2 : 1;
  const roundedRaw = (x: number, d: number) =>
    Math.abs(x - Math.round(x)) < 1e-6 ? String(Math.round(x)) : x.toFixed(d);
  const rounded = roundedRaw(v, decimals);

  if (key.includes('uL') || key.endsWith('_uL')) return `${rounded} µL`;
  if (key.endsWith('_g_per_L')) return `${rounded} g/L`;
  if (key.endsWith('_mM')) return `${rounded} mM`;
  if (key.includes('mm')) return `${rounded} mm`;
  if (key.includes('reps')) return `${rounded} reps`;
  return rounded;
}

export type DesignParamEntry = {
  key: string;
  label: string;
  display: string;
};

/** One row per key, in the same order as in the iteration `params` object. */
export function designParamEntries(params: Record<string, number> | null | undefined): DesignParamEntry[] {
  if (!params || Object.keys(params).length === 0) return [];
  return Object.keys(params).map((key) => ({
    key,
    label: keyToLabel(key),
    display: formatParamValue(key, params[key]!),
  }));
}

/** One line for summaries and inline text (e.g. "Cell volume: 32.6 µL · …"). */
export function formatDesignParamsInline(params: Record<string, number> | null | undefined): string {
  const entries = designParamEntries(params);
  if (entries.length === 0) return '';
  return entries.map((e) => `${e.label}: ${e.display}`).join(' · ');
}

/** Plotly hover HTML (uses <br>). */
export function formatDesignParamsPlotlyHtml(params: Record<string, number> | null | undefined): string {
  const entries = designParamEntries(params);
  if (entries.length === 0) return '<b>Experimental design</b><br><i>No parameters</i>';
  return (
    '<b>Experimental design</b><br>' +
    entries.map((e) => `<b>${e.label}</b><br>${e.display}`).join('<br><br>')
  );
}
