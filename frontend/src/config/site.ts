/**
 * Matches the GitHub repository name and pyproject.toml [project].name.
 * @see https://github.com/keltoumboukra/closed-loop-ai-scientist-cell-culture-workcell
 */
export const REPOSITORY_NAME = 'closed-loop-ai-scientist-cell-culture-workcell';

/** Legacy full app name (e.g. docs, defaults). Main UI uses page name + mascot in the header. */
export const SITE_DISPLAY_TITLE = 'Closed Loop AI Scientist Cell Culture Dashboard';

/** Suffix for document.title: "<Page> · {this}" */
export const SITE_BROWSER_TAB_SUFFIX = 'Closed-loop cell culture';

/** @deprecated Tagline removed from layout; kept for reference or future use. */
export const SITE_TAGLINE =
  'Monitor iteration runs, growth metrics, and plate layouts for closed-loop experiments.';

/**
 * Public GitHub URL. Override with `VITE_GITHUB_REPO_URL` in `.env` for forks.
 */
export const GITHUB_REPO_URL =
  import.meta.env.VITE_GITHUB_REPO_URL ||
  `https://github.com/keltoumboukra/${REPOSITORY_NAME}`;
