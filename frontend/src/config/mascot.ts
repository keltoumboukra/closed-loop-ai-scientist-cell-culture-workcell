/**
 * Public mascot URLs (served from frontend/public/mascot).
 * Source assets: assets/mascot/manual_exports/ (sync via scripts/sync_mascot_manual_exports.py).
 */

export const MASCOT_URLS = {
  dashboard: '/mascot/dashboard.png',
  iteration: '/mascot/iteration.png',
  history: '/mascot/history.png',
  compare: '/mascot/compare.png',
  error: '/mascot/error.png',
  empty: '/mascot/empty.png',
  collaboration: '/mascot/collaboration.png',
  /** Face-only mark; full set lives under /mascot/exports/ */
  head: '/mascot/exports/loopy-head.png',
} as const;

export type MascotVariant = keyof typeof MASCOT_URLS;

/** Variants used for page headers (full-body scene art). */
export type MascotPageVariant = Exclude<MascotVariant, 'head' | 'collaboration' | 'error'>;

export function mascotSrc(v: MascotVariant): string {
  return MASCOT_URLS[v];
}
