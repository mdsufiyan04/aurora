import React from 'react';
import { useAppStore } from '../../store/useAppStore';

export function TopBar() {
  const { response } = useAppStore();
  
  return (
    <div className="h-12 border-b border-bridge-border flex items-center justify-between px-4 bg-bridge-deep shrink-0">
      <div className="flex items-center gap-3">
        <span className="text-[15px] font-medium tracking-wider text-bridge-text">AURORA</span>
        <span className="text-[11px] text-bridge-dim">Antarctic Navigation Decision Support</span>
      </div>
      
      <div className="text-[12px] text-bridge-faint mono">
        {response?.run_id ? `RUN ID: ${response.run_id}` : ''}
      </div>
      
      <div className="flex items-center gap-4">
        <div className="px-2 py-0.5 border border-bridge-warning text-bridge-warning text-[10px] uppercase font-medium">
          ADVISORY ONLY
        </div>
        <div className="flex items-center gap-1.5">
          <div className="status-dot bg-bridge-success"></div>
          <span className="text-[11px] mono uppercase text-bridge-text">ONLINE</span>
        </div>
      </div>
    </div>
  );
}
