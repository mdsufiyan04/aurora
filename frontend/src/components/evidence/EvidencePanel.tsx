import React from 'react';
import { useAppStore } from '../../store/useAppStore';

export function EvidencePanel() {
  const { response, loading, selectedRouteLabel } = useAppStore();

  if (loading) {
    return (
      <div className="panel flex flex-col border-l-0 flex-1" data-testid="evidence-panel">
        <div className="panel-header">WHY THIS ROUTE</div>
        <div className="p-4 space-y-4 animate-pulse">
          <div className="h-4 w-3/4 bg-bridge-surface"></div>
          <div className="h-4 w-1/2 bg-bridge-surface ml-4"></div>
          <div className="h-4 w-2/3 bg-bridge-surface mt-6"></div>
          <div className="h-4 w-1/3 bg-bridge-surface ml-4"></div>
        </div>
      </div>
    );
  }

  if (!response || !response.evidence) {
    return (
      <div className="panel flex flex-col border-l-0 flex-1" data-testid="evidence-panel">
        <div className="panel-header">WHY THIS ROUTE</div>
        <div className="p-4 text-center text-bridge-dim text-[11px] mono uppercase tracking-wider py-8">
          Query submitted will appear here
        </div>
      </div>
    );
  }

  // Use the evidence block, even if user selected a different route manually.
  // In Phase 2 this will dynamically fetch evidence for the selected route.
  const ev = response.evidence;
  
  console.log('why_selected array:', ev?.why_selected);
  console.log('why_selected length:', ev?.why_selected?.length);
  console.log('First item:', ev?.why_selected?.[0]);

  // Show a notice if we are looking at a route that wasn't the AI's primary selection
  const isAltRoute = selectedRouteLabel !== response.selected_route?.label;

  return (
    <div className="panel flex flex-col border-l-0 flex-1 border-t-0 overflow-y-auto" data-testid="evidence-panel">
      
      {isAltRoute && (
        <div className="bg-bridge-warning/10 border-b border-bridge-warning text-bridge-warning px-4 py-2 text-[11px] font-sans">
          ⚠ Showing evidence for AI recommended route ({response.selected_route?.label})
        </div>
      )}

      {/* WHY SELECTED */}
      <div className="panel-header border-t-0 bg-bridge-base/95 sticky top-0">WHY {response.selected_route?.label || 'THIS ROUTE'}</div>
      <div className="p-4 flex flex-col gap-4">
        {(ev.why_selected || []).map((item: any, i: number) => (
          <div key={i} className="flex flex-col gap-1" data-testid="why-selected-item">
            <div className="flex items-start gap-1.5">
              <span className="text-bridge-success text-[14px] leading-none mt-0.5">✓</span>
              <span className="text-[13px] text-bridge-text font-medium font-sans">{item.claim}</span>
            </div>
            {item.evidence && (
              <div className="pl-[22px] text-[12px] mono text-bridge-dim">
                {item.evidence}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* WHY REJECTED */}
      {ev.why_rejected && ev.why_rejected.length > 0 && (
        <div data-testid="why-rejected">
          <div className="panel-header bg-bridge-base/95 sticky top-0">WHY OTHERS WERE REJECTED</div>
          <div className="p-4 flex flex-col gap-4">
            {ev.why_rejected.map((item: any, i: number) => (
              <div key={i} className="flex flex-col gap-1" data-testid="why-rejected-item">
                <div className="text-[12px] font-medium font-sans text-bridge-text">{item.label}</div>
                {item.evidence && (
                  <div className="text-[11px] mono text-bridge-dim">
                    {item.evidence}
                  </div>
                )}
                {item.trade_off && (
                  <div className="text-[11px] font-sans text-bridge-dim">
                    {item.trade_off}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* PROVENANCE */}
      {ev.provenance && ev.provenance.datasets && (
        <>
          <div className="panel-header bg-bridge-base/95 sticky top-0">DATA PROVENANCE</div>
          <div className="p-4 flex flex-col gap-1.5">
            {ev.provenance.datasets.map((ds: any, idx: number) => (
              <div key={idx} className="grid grid-cols-[1fr_auto] gap-4 items-center">
                <div className="text-[11px] font-sans text-bridge-dim truncate">{ds.name}</div>
                <div className="text-[11px] mono text-bridge-faint whitespace-nowrap">{ds.valid_time || ds.version}</div>
              </div>
            ))}
          </div>
        </>
      )}

    </div>
  );
}
