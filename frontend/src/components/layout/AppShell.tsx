import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { SiteMainHeader } from './SiteMainHeader';

export function AppShell() {
  const { pathname } = useLocation();
  const hideSiteHeader = pathname === '/oops';

  return (
    <div className="flex h-screen bg-background text-foreground">
      <Sidebar />
      <main className="flex min-h-0 flex-1 flex-col overflow-auto p-6">
        {hideSiteHeader ? null : <SiteMainHeader />}
        <div className="flex min-h-0 flex-1 flex-col">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
