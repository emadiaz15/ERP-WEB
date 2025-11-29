import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

const queryClient = new QueryClient();

export function withReactQueryProvider(App) {
  return function AppWithQueryProvider(props) {
    return (
      <QueryClientProvider client={queryClient}>
        <App {...props} />
      </QueryClientProvider>
    );
  };
}
