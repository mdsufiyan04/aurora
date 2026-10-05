import React from 'react';
import { useAppStore } from '../../store/useAppStore';

export function QueryPanel() {
  const { query, setQuery, submitQuery, loading, error, recentQueries } = useAppStore();

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submitQuery();
    }
  };

  const examples = [
    "Safe route Bharati → Maitri",
    "Fastest route to Maitri",
    "Compare all routes",
    "Sea-ice forecast"
  ];

  return (
    <div className="panel h-full flex flex-col border-r-0">
      <div className="panel-header">MISSION QUERY</div>
      <div className="p-3 flex flex-col gap-4">
        
        <div className="flex flex-col gap-2">
          <textarea
            className="w-full bg-bridge-deep border border-bridge-border px-3 py-2 text-bridge-text text-[13px] focus:outline-none focus:border-bridge-muted resize-none"
            rows={3}
            placeholder="Ask about Antarctic navigation..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            className={`w-full py-2 text-[12px] font-medium uppercase tracking-wide transition-colors ${
              loading 
                ? 'bg-bridge-muted text-bridge-faint cursor-not-allowed' 
                : 'bg-bridge-primary text-bridge-deep hover:bg-bridge-ice'
            }`}
            onClick={submitQuery}
            disabled={loading || !query.trim()}
          >
            {loading ? 'COMPUTING...' : 'ANALYZE'}
          </button>
        </div>

        {error && (
          <div className="p-2 border border-bridge-danger/50 bg-bridge-danger/10 text-bridge-danger text-[12px]">
            {error}
          </div>
        )}

        <div className="flex flex-col gap-2 mt-2">
          <div className="text-[11px] text-bridge-faint uppercase tracking-wider">EXAMPLES</div>
          <div className="flex flex-wrap gap-2">
            {examples.map(ex => (
              <button
                key={ex}
                className="border border-bridge-border px-2 py-1.5 text-[11px] text-bridge-dim hover:bg-bridge-surface hover:text-bridge-text transition-colors text-left"
                onClick={() => {
                  setQuery(ex);
                  setTimeout(submitQuery, 50);
                }}
                disabled={loading}
              >
                {ex}
              </button>
            ))}
          </div>
        </div>

        {recentQueries.length > 0 && (
          <div className="flex flex-col gap-2 mt-4">
            <div className="text-[11px] text-bridge-faint uppercase tracking-wider">RECENT</div>
            <div className="flex flex-col gap-1">
              {recentQueries.map((rq, idx) => (
                <button
                  key={idx}
                  className="text-left px-2 py-1.5 text-[12px] text-bridge-dim hover:bg-bridge-surface hover:text-bridge-text transition-colors truncate"
                  onClick={() => {
                    setQuery(rq);
                    setTimeout(submitQuery, 50);
                  }}
                  disabled={loading}
                >
                  {rq}
                </button>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
