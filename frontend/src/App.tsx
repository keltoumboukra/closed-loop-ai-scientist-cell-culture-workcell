import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TooltipProvider } from '@/components/ui/tooltip';
import { ErrorBoundary } from '@/components/feedback/ErrorBoundary';
import { AppShell } from '@/components/layout/AppShell';
import { Dashboard } from '@/pages/Dashboard';
import { IterationView } from '@/pages/IterationView';
import { History } from '@/pages/History';
import { Compare } from '@/pages/Compare';
import { Oops } from '@/pages/Oops';
import type { ReactNode } from 'react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
});

function RoutedErrorBoundary({ children }: { children: ReactNode }) {
  const location = useLocation();
  // Remount after navigation so a recovered tree is not stuck behind hasError (and new key on each nav).
  return (
    <ErrorBoundary key={`${location.pathname}:${location.key}`}>{children}</ErrorBoundary>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <BrowserRouter>
          <RoutedErrorBoundary>
            <Routes>
              <Route element={<AppShell />}>
                <Route path="/" element={<Dashboard />} />
                <Route path="/iterations/:iterationId" element={<IterationView />} />
                <Route path="/history" element={<History />} />
                <Route path="/compare" element={<Compare />} />
                <Route path="/oops" element={<Oops />} />
              </Route>
            </Routes>
          </RoutedErrorBoundary>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
}
