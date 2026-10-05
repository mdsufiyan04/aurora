import React from 'react';
import { useAppStore } from '../../store/useAppStore';

const ROUTE_COLORS: Record<string, string> = {
  FASTEST: 'border-bridge-danger text-bridge-danger',
  SAFEST: 'border-bridge-success text-bridge-success',
  BALANCED: 'border-bridge-warning text-bridge-warning',
  FUEL_EFFICIENT: 'border-bridge-dim text-bridge-dim'
};

export function RouteSelector() {
  const { response, selectedRouteLabel, selectRoute, loading } = useAppStore();

  if (loading) {
    return (
      <div className="panel flex flex-col p-3 mb-2 animate-pulse">
        <div className="h-2 w-16 bg-bridge-muted mb-3"></div>
        <div className="flex gap-2">
          <div className="h-6 w-20 bg-bridge-surface border border-bridge-border"></div>
          <div className="h-6 w-20 bg-bridge-surface border border-bridge-border"></div>
          <div className="h-6 w-20 bg-bridge-surface border border-bridge-border"></div>
        </div>
      </div>
    );
  }

  if (!response?.routes || response.routes.length === 0) {
    return null;
  }

  return (
    <div className="panel flex flex-col p-3 mb-2 border-l-0">
      <div className="text-[10px] uppercase tracking-wider text-bridge-dim mb-2 font-sans font-medium">ROUTES</div>
      <div className="flex flex-wrap gap-2">
        {response.routes.map(r => {
          const isSelected = r.label === selectedRouteLabel;
          const colorClass = isSelected ? 'border-bridge-primary text-bridge-text bg-bridge-surface' : 'border-bridge-border text-bridge-dim hover:bg-bridge-surface hover:text-bridge-text';
          
          return (
            <button
              key={r.label}
              data-testid="route-button"
              className={`px-2 py-1 text-[10px] mono uppercase border transition-colors ${colorClass}`}
              onClick={() => selectRoute(r.label)}
            >
              {r.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
