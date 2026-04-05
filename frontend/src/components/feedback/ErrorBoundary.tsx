import { Component, type ErrorInfo, type ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import type { OopsLocationState } from '@/pages/Oops';

type Props = { children: ReactNode };

type State = { hasError: boolean; error: Error | null };

/**
 * Catches render errors and sends users to /oops instead of an inline card.
 * Remount when the route changes (see App key on pathname) so navigation recovers.
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('UI error boundary:', error, info.componentStack);
  }

  render() {
    if (this.state.hasError && this.state.error) {
      const state: OopsLocationState = { message: this.state.error.message };
      return <Navigate to="/oops" replace state={state} />;
    }
    return this.props.children;
  }
}
