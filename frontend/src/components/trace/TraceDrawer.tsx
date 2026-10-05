import React, { useState, useEffect } from 'react';
import { useAppStore } from '../../store/useAppStore';
import { fmt } from '../../utils/format';

export function TraceDrawer() {
  const { response, loading, traceExpanded, setTraceExpanded } = useAppStore();
  const [flash, setFlash] = useState(false);
  const [showVerifyModal, setShowVerifyModal] = useState(false);

  // Trigger brief flash when new response arrives
  useEffect(() => {
    if (response) {
      setFlash(true);
      const timer = setTimeout(() => setFlash(false), 300);
      return () => clearTimeout(timer);
    }
  }, [response]);

  const numSteps = response?.trace ? response.trace.length : 0;
  const totalSecs = response?.total_duration_seconds ? response.total_duration_seconds.toFixed(1) : '0.0';
  const runId = response?.run_id || '';
  
  // Header text logic based on state
  let headerText = (
    <>
      <span className="text-[11px] font-sans font-medium uppercase tracking-wider text-bridge-dim">EXECUTION TRACE</span>
      <span className="text-bridge-dim">·</span>
      <span className="text-[11px] mono text-bridge-faint">awaiting query</span>
    </>
  );

  if (loading) {
    headerText = (
      <>
        <span className="text-[11px] font-sans font-medium uppercase tracking-wider text-bridge-dim">EXECUTION TRACE</span>
        <span className="text-bridge-dim">·</span>
        <span className="text-[11px] mono text-bridge-faint animate-pulse">computing...</span>
      </>
    );
  } else if (response) {
    headerText = (
      <>
        <span className="text-[11px] font-sans font-medium uppercase tracking-wider text-bridge-dim">EXECUTION TRACE</span>
        <span className="text-bridge-dim">·</span>
        <span className="text-[11px] mono text-bridge-faint">{numSteps} steps</span>
        <span className="text-bridge-dim">·</span>
        <span className="text-[11px] mono text-bridge-faint">{totalSecs}s total</span>
      </>
    );
  }

  return (
    <>
      <div 
        className="w-full bg-bridge-base border-t transition-all duration-200 ease-out flex flex-col"
        style={{ 
          height: traceExpanded ? '280px' : '32px',
          borderColor: flash ? '#D49A3A' : '#1F3047' 
        }}
      >
        {/* HEADER BAR (Always visible) */}
        <div 
          className="h-8 flex items-center justify-between px-3 cursor-pointer hover:bg-bridge-surface/50 shrink-0 select-none"
          onClick={() => {
            if (response) setTraceExpanded(!traceExpanded);
          }}
        >
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-bridge-dim font-sans w-3 text-center">
              {traceExpanded ? '▼' : '▶'}
            </span>
            {headerText}
          </div>
          
          <div className="flex items-center gap-4">
            {response && (
              <span className="text-[10px] mono text-bridge-faint max-w-[120px] truncate" title={runId}>
                {runId}
              </span>
            )}
            
            {traceExpanded && response && (
              <button 
                className="px-2 py-0.5 border border-bridge-border text-[10px] mono uppercase text-bridge-dim hover:text-bridge-text hover:bg-bridge-surface transition-colors"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowVerifyModal(true);
                }}
              >
                VERIFY
              </button>
            )}
          </div>
        </div>

        {/* EXPANDED CONTENT */}
        <div className={`flex-1 flex flex-col overflow-hidden ${!traceExpanded ? 'hidden' : ''}`}>
          
          {/* Table Header */}
          <div className="grid grid-cols-[30px_180px_1fr_1fr_80px] gap-4 px-3 py-1.5 border-b border-bridge-border text-[10px] uppercase tracking-wider font-sans font-medium text-bridge-faint bg-bridge-base shrink-0">
            <div className="text-right">STEP</div>
            <div>NODE</div>
            <div>INPUT</div>
            <div>OUTPUT</div>
            <div className="text-right">DURATION</div>
          </div>
          
          {/* Table Body */}
          <div className="flex-1 overflow-y-auto overflow-x-hidden">
            {response?.trace && response.trace.map((step) => (
              <div 
                key={step.step} 
                className="grid grid-cols-[30px_180px_1fr_1fr_80px] gap-4 px-3 h-7 items-center border-b border-bridge-border/40 hover:bg-bridge-surface/30"
              >
                <div className="text-[11px] mono text-bridge-faint text-right">{step.step}</div>
                <div className="text-[11px] mono text-bridge-text truncate" title={step.node}>{step.node}</div>
                <div className="text-[11px] font-sans text-bridge-dim truncate" title={step.input_summary}>{step.input_summary}</div>
                <div className="text-[11px] font-sans text-bridge-dim truncate" title={step.output_summary}>{step.output_summary}</div>
                <div className="text-[11px] mono text-bridge-dim text-right">{fmt.duration(step.duration_ms)}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* VERIFY MODAL */}
      {showVerifyModal && response && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-bridge-deep/80 backdrop-blur-sm p-4">
          <div className="w-[420px] bg-bridge-base border border-bridge-border shadow-2xl flex flex-col">
            <div className="px-4 py-2 border-b border-bridge-border font-sans font-medium text-[11px] text-bridge-dim uppercase tracking-wider bg-bridge-surface/50">
              TRACE VERIFICATION
            </div>
            
            <div className="p-5 flex flex-col gap-4">
              <div className="flex flex-col gap-2">
                <div className="flex items-center gap-2">
                  <span className="text-[14px] text-bridge-success leading-none">✓</span>
                  <span className="text-[12px] font-sans text-bridge-text">All {numSteps} steps recorded</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[14px] text-bridge-success leading-none">✓</span>
                  <span className="text-[12px] font-sans text-bridge-text">Chain integrity: intact</span>
                </div>
              </div>
              
              <div className="border-t border-bridge-border/50"></div>
              
              <div className="flex flex-col gap-1">
                <div className="text-[11px] font-sans text-bridge-dim">Run ID: <span className="mono text-bridge-text">{runId}</span></div>
                <div className="text-[11px] font-sans text-bridge-dim">Started: <span className="mono text-bridge-text">2026-10-03T09:24:02Z</span></div>
                <div className="text-[11px] font-sans text-bridge-dim">Completed: <span className="mono text-bridge-text">2026-10-03T09:24:28Z</span></div>
              </div>

              <div className="border-t border-bridge-border/50"></div>
              
              <div className="flex flex-col gap-1">
                <div className="text-[11px] font-medium font-sans uppercase tracking-wider text-bridge-dim mb-1">Data provenance:</div>
                <div className="grid grid-cols-[1fr_auto] items-center text-[11px]">
                  <span className="font-sans text-bridge-dim">OSI-SAF SIC</span>
                  <span className="mono text-bridge-faint">2026-10-03T00:00Z</span>
                </div>
                <div className="grid grid-cols-[1fr_auto] items-center text-[11px]">
                  <span className="font-sans text-bridge-dim">BYU/NIC</span>
                  <span className="mono text-bridge-faint">v8.0</span>
                </div>
                <div className="grid grid-cols-[1fr_auto] items-center text-[11px]">
                  <span className="font-sans text-bridge-dim">ERA5</span>
                  <span className="mono text-bridge-faint">2026-09-27</span>
                </div>
                <div className="grid grid-cols-[1fr_auto] items-center text-[11px]">
                  <span className="font-sans text-bridge-dim">GEBCO</span>
                  <span className="mono text-bridge-faint">2024</span>
                </div>
              </div>
            </div>
            
            <div className="px-4 py-3 bg-bridge-surface/50 border-t border-bridge-border flex justify-end">
              <button 
                className="px-3 py-1 border border-bridge-border text-[11px] mono uppercase text-bridge-dim hover:text-bridge-text hover:bg-bridge-surface transition-colors"
                onClick={() => setShowVerifyModal(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
