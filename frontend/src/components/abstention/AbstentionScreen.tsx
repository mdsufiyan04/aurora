import React from 'react';
import { useAppStore } from '../../store/useAppStore';

export function AbstentionScreen() {
  const { response, setResponse } = useAppStore();

  if (!response || !response.abstained) return null;

  const handleAcknowledge = () => {
    // For demo purposes, we can un-abstain or simply close the screen
    setResponse({ ...response, abstained: false });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-bridge-deep/90 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl panel border-bridge-warning flex flex-col shadow-2xl">
        
        <div className="p-8 flex flex-col gap-6">
          <div className="flex items-start gap-4">
            <div className="text-[32px] text-bridge-warning leading-none">⚠</div>
            <div className="flex flex-col gap-1">
              <h2 className="text-[18px] font-medium font-sans text-bridge-warning tracking-wide uppercase">
                NO ROBUST RECOMMENDATION
              </h2>
              <div className="text-[13px] font-sans text-bridge-text mt-2">
                Reason: {response.abstention_reason || "Uncertainty exceeds safety thresholds."}
              </div>
            </div>
          </div>

          <div className="border-t border-bridge-border"></div>

          {response.evidence?.abstention_rules && (
            <div className="flex flex-col gap-2">
              <div className="text-[11px] font-medium uppercase tracking-wider text-bridge-text">Contributing factors:</div>
              <ul className="flex flex-col gap-1.5">
                {response.evidence.abstention_rules.map((rule: any, idx: number) => (
                  <li key={idx} className="flex gap-2 text-[13px] text-bridge-dim font-sans">
                    <span className="text-bridge-faint">•</span>
                    <span>{rule.description || JSON.stringify(rule)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="border-t border-bridge-border"></div>

          <div className="flex flex-col gap-2">
            <div className="text-[11px] font-medium uppercase tracking-wider text-bridge-text">Action required:</div>
            <div className="text-[13px] text-bridge-dim font-sans">
              Await updated Sentinel-1 observation.<br/>
              Human approval required before proceeding.
            </div>
          </div>
        </div>

        <div className="bg-bridge-surface px-8 py-4 flex gap-4 border-t border-bridge-border justify-end">
          <button 
            className="px-4 py-2 border border-bridge-border text-[12px] font-medium uppercase tracking-wider text-bridge-dim hover:text-bridge-text hover:bg-bridge-muted transition-colors"
            onClick={() => alert("Raw data viewer not implemented in MVP")}
          >
            View raw data
          </button>
          <button 
            className="px-4 py-2 border border-bridge-warning text-[12px] font-medium uppercase tracking-wider text-bridge-warning hover:bg-bridge-warning/10 transition-colors"
            onClick={handleAcknowledge}
          >
            Acknowledge
          </button>
        </div>

      </div>
    </div>
  );
}
