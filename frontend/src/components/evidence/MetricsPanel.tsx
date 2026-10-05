import React from 'react';
import { useAppStore } from '../../store/useAppStore';
import { fmt } from '../../utils/format';

export function MetricsPanel() {
  const { response, selectedRouteLabel, loading } = useAppStore();

  if (loading) {
    return (
      <div className="panel flex flex-col border-l-0 border-b-0">
        <div className="panel-header">SELECTED ROUTE</div>
        <div className="p-4 flex flex-col gap-4 animate-pulse">
          <div className="h-6 w-32 bg-bridge-muted"></div>
          <div className="h-4 w-24 bg-bridge-surface"></div>
          <div className="h-2 w-full bg-bridge-surface mt-2"></div>
          <div className="border-t border-bridge-border my-2"></div>
          <div className="grid grid-cols-2 gap-y-2">
            <div className="h-4 w-16 bg-bridge-surface"></div>
            <div className="h-4 w-20 bg-bridge-muted justify-self-end"></div>
            <div className="h-4 w-24 bg-bridge-surface"></div>
            <div className="h-4 w-16 bg-bridge-muted justify-self-end"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!response) {
    return (
      <div className="panel flex flex-col border-l-0 border-b-0">
        <div className="panel-header">SELECTED ROUTE</div>
        <div className="p-4 text-center text-bridge-dim text-[11px] mono uppercase tracking-wider py-8">
          AWAITING QUERY
        </div>
      </div>
    );
  }

  const route = response.routes.find(r => r.label === selectedRouteLabel) || response.selected_route;
  
  if (!route) return null;

  const robustRatio = route.robust_feasibility ?? 1.0;
  const robustText = `${Math.round(robustRatio * 50)} of 50 scenarios`;

  return (
    <div className="panel flex flex-col border-l-0 border-b-0">
      <div className="panel-header">SELECTED ROUTE</div>
      
      <div className="p-4 flex flex-col">
        <div className="text-[22px] font-medium text-bridge-text font-sans tracking-wide">
          {route.label}
        </div>
        
        <div className="mt-4 flex flex-col gap-1">
          <div className="flex justify-between items-end">
            <span className="text-[11px] uppercase tracking-wide text-bridge-dim font-sans font-medium">ROBUST FEASIBILITY</span>
            <span className="text-[13px] mono text-bridge-text">{fmt.percent(robustRatio)}</span>
          </div>
          
          <div className="w-full h-1.5 bg-bridge-muted overflow-hidden flex">
            <div 
              className="h-full bg-bridge-success" 
              style={{ width: `${robustRatio * 100}%` }}
            ></div>
          </div>
          <div className="text-[10px] text-bridge-dim font-sans mt-0.5">
            {robustText}
          </div>
        </div>
        
        <div className="border-t border-bridge-border my-4"></div>
        
        <div className="grid grid-cols-[1fr_auto] gap-y-2 gap-x-4 items-center">
          <div className="text-[11px] uppercase tracking-wide text-bridge-dim font-sans font-medium">DISTANCE</div>
          <div className="text-[13px] mono text-bridge-text">{fmt.km(route.distance_km)}</div>
          
          <div className="text-[11px] uppercase tracking-wide text-bridge-dim font-sans font-medium">TRAVEL TIME</div>
          <div className="text-[13px] mono text-bridge-text">{fmt.hours(route.travel_time_hours)}</div>
          
          <div className="text-[11px] uppercase tracking-wide text-bridge-dim font-sans font-medium">FUEL</div>
          <div className="text-[13px] mono text-bridge-text">{fmt.tonnes(route.fuel_tonnes)}</div>
          
          <div className="text-[11px] uppercase tracking-wide text-bridge-dim font-sans font-medium">EXPECTED RISK</div>
          <div className="text-[13px] mono text-bridge-text">{fmt.risk(route.expected_risk)}</div>
          
          {route.p90_risk !== null && route.p90_risk !== undefined && (
            <>
              <div className="text-[11px] uppercase tracking-wide text-bridge-dim font-sans font-medium">P90 RISK</div>
              <div className="text-[13px] mono text-bridge-text">{fmt.risk(route.p90_risk)}</div>
            </>
          )}
          
          {route.p95_risk !== null && route.p95_risk !== undefined && (
            <>
              <div className="text-[11px] uppercase tracking-wide text-bridge-dim font-sans font-medium">P95 RISK</div>
              <div className="text-[13px] mono text-bridge-text">{fmt.risk(route.p95_risk)}</div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
