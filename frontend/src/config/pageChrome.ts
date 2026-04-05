import type { MascotVariant } from '@/config/mascot';

/** Primary heading and mascot for the current route (main column header). */
export function pageChromeFromPath(pathname: string): { title: string; mascot: MascotVariant } {
  if (pathname === '/') {
    return { title: 'Dashboard', mascot: 'dashboard' };
  }
  if (pathname.startsWith('/iterations/')) {
    return { title: 'Iteration', mascot: 'iteration' };
  }
  if (pathname === '/history') {
    return { title: 'History', mascot: 'history' };
  }
  if (pathname === '/compare') {
    return { title: 'Compare iterations', mascot: 'compare' };
  }
  return { title: 'Dashboard', mascot: 'dashboard' };
}
