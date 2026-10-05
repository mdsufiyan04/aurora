export interface RouteOption {
  label: 'FASTEST' | 'SAFEST' | 'BALANCED' | 'FUEL_EFFICIENT';
  geometry: number[][];      // [[lon, lat], ...]
  distance_km: number;
  travel_time_hours: number;
  fuel_tonnes: number;
  expected_risk: number;
  max_sic: number;
  robust_feasibility: number;
  feasibility_detail: string;
  p90_risk: number;
  p95_risk: number;
}

export interface TraceStep {
  step: number;
  node: string;
  timestamp: string;
  input_summary: string;
  output_summary: string;
  duration_ms: number;
}

export interface IntentResult {
  intent: string;
  confidence: number;
  slots: Record<string, any>;
}

export interface AnalysisResponse {
  run_id: string;
  query: string;
  intent: IntentResult;
  routes: RouteOption[];
  selected_route: RouteOption | null;
  abstained: boolean;
  abstention_reason: string | null;
  evidence: any;
  trace: TraceStep[];
  total_duration_seconds: number;
  sensitivity: any;
  icebergs: any[];
}
