import React from 'react';
import { useAppStore } from '../../store/useAppStore';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip as RechartsTooltip } from 'recharts';
import { fmt } from '../../utils/format';

const ROUTE_COLORS: Record<string, string> = {
  FASTEST: '#C1444A',
  SAFEST: '#4A8B5E',
  BALANCED: '#D49A3A',
  FUEL_EFFICIENT: '#7D8FA3'
};

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-bridge-surface border border-bridge-border px-2 py-1 flex flex-col gap-1">
        <div className="text-[10px] font-medium text-bridge-text uppercase tracking-wider">{data.label}</div>
        <div className="text-[11px] mono text-bridge-dim">
          Fuel: {fmt.tonnes(data.fuel)}
        </div>
        <div className="text-[11px] mono text-bridge-dim">
          Safety: {data.safety.toFixed(1)}
        </div>
      </div>
    );
  }
  return null;
};

const CustomDot = (props: any) => {
  const { cx, cy, payload, onClick } = props;
  const isSelected = payload.isSelected;
  
  return (
    <circle 
      data-testid="pareto-point"
      cx={cx} 
      cy={cy} 
      r={isSelected ? 6 : 4}
      fill={payload.color}
      stroke={isSelected ? '#FFFFFF' : 'none'}
      strokeWidth={isSelected ? 1.5 : 0}
      cursor="pointer"
      onClick={(e) => onClick && onClick(payload, e)}
    />
  );
};

export function ParetoPlot() {
  const { response, selectedRouteLabel, selectRoute, loading } = useAppStore();

  if (loading || !response || response.routes.length === 0) {
    return null;
  }

  const data = response.routes.map(r => ({
    label: r.label,
    fuel: r.fuel_tonnes,
    safety: 100 - (r.expected_risk * 100), // convert risk to safety score
    color: ROUTE_COLORS[r.label] || '#7D8FA3',
    isSelected: r.label === selectedRouteLabel
  }));

  // Add domain padding
  const fuelMin = Math.min(...data.map(d => d.fuel));
  const fuelMax = Math.max(...data.map(d => d.fuel));
  const safetyMin = Math.min(...data.map(d => d.safety));
  const safetyMax = Math.max(...data.map(d => d.safety));

  const fPadding = (fuelMax - fuelMin) * 0.2 || 10;
  const sPadding = (safetyMax - safetyMin) * 0.2 || 10;

  return (
    <div className="panel flex flex-col border-l-0 border-t-0 h-48 shrink-0">
      <div className="panel-header border-t-0">ROUTE TRADE-OFFS</div>
      <div className="flex-1 p-2 pb-0 relative">
        <div className="absolute top-2 left-10 text-[9px] text-bridge-faint mono tracking-wider">SAFETY ↑</div>
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 15, right: 15, bottom: 0, left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1F3047" vertical={false} />
            <XAxis 
              type="number" 
              dataKey="fuel" 
              name="Fuel" 
              domain={[fuelMin - fPadding, fuelMax + fPadding]}
              tick={{ fontSize: 10, fill: '#4A5C73', fontFamily: 'JetBrains Mono, monospace' }}
              tickFormatter={(v) => Math.round(v).toString()}
              axisLine={{ stroke: '#1F3047' }}
              tickLine={{ stroke: '#1F3047' }}
            />
            <YAxis 
              type="number" 
              dataKey="safety" 
              name="Safety" 
              domain={[safetyMin - sPadding, safetyMax + sPadding]}
              tick={{ fontSize: 10, fill: '#4A5C73', fontFamily: 'JetBrains Mono, monospace' }}
              tickFormatter={(v) => Math.round(v).toString()}
              axisLine={{ stroke: '#1F3047' }}
              tickLine={{ stroke: '#1F3047' }}
            />
            <RechartsTooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3', stroke: '#1F3047' }} />
            <Scatter 
              name="Routes" 
              data={data} 
              shape={<CustomDot onClick={(data: any) => selectRoute(data.label)} />}
            />
          </ScatterChart>
        </ResponsiveContainer>
        <div className="absolute bottom-1 right-2 text-[9px] text-bridge-faint mono tracking-wider text-right bg-bridge-base/80 px-1">
          FUEL (t) →
        </div>
      </div>
    </div>
  );
}
