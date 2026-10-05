import React from 'react';
import { ConsoleLayout } from './components/layout/ConsoleLayout';
import { TopBar } from './components/layout/TopBar';
import { StatusBar } from './components/layout/StatusBar';
import { QueryPanel } from './components/query/QueryPanel';
import { PolarMap } from './components/map/PolarMap';
import { EvidencePanel } from './components/evidence/EvidencePanel';
import { MetricsPanel } from './components/evidence/MetricsPanel';
import { RouteSelector } from './components/evidence/RouteSelector';
import { ParetoPlot } from './components/pareto/ParetoPlot';
import { TraceDrawer } from './components/trace/TraceDrawer';
import { AbstentionScreen } from './components/abstention/AbstentionScreen';
import { useAppStore } from './store/useAppStore';

function App() {
  const { response, loading } = useAppStore();
  
  return (
    <ConsoleLayout>
      <TopBar />
      <div className="grid grid-cols-[280px_1fr_340px] flex-1 overflow-hidden">
        <QueryPanel />
        <PolarMap />
        <div className="flex flex-col h-full overflow-y-auto bg-bridge-deep">
          {response && !response.abstained && !loading && (
            <>
              <RouteSelector />
              <MetricsPanel />
              <EvidencePanel />
              <ParetoPlot />
            </>
          )}
          {loading && (
             <>
              <RouteSelector />
              <MetricsPanel />
              <EvidencePanel />
            </>
          )}
          {!response && !loading && (
            <>
              <MetricsPanel />
              <EvidencePanel />
            </>
          )}
        </div>
      </div>
      <TraceDrawer />
      <StatusBar />
      <AbstentionScreen />
    </ConsoleLayout>
  );
}

export default App;
