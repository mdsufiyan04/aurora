import { create } from 'zustand';
import type { AnalysisResponse } from '../api/types';
import { analyze as analyzeApi } from '../api/client';

interface AppState {
  query: string;
  response: AnalysisResponse | null;
  loading: boolean;
  error: string | null;
  selectedRouteLabel: string | null;
  recentQueries: string[];
  
  setQuery: (q: string) => void;
  submitQuery: () => Promise<void>;
  setResponse: (r: AnalysisResponse) => void;
  setError: (e: string | null) => void;
  selectRoute: (label: string) => void;
  setTraceExpanded: (v: boolean) => void;
  reset: () => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  query: '',
  response: null,
  loading: false,
  error: null,
  selectedRouteLabel: null,
  recentQueries: [],
  traceExpanded: false,
  
  setQuery: (q) => set({ query: q }),
  
  submitQuery: async () => {
    const { query, recentQueries } = get();
    if (!query.trim()) return;
    
    set({ loading: true, error: null });
    try {
      const response = await analyzeApi(query);
      
      const newRecent = [query, ...recentQueries.filter(q => q !== query)].slice(0, 5);
      
      set({ 
        response, 
        selectedRouteLabel: response.selected_route?.label || null,
        loading: false,
        recentQueries: newRecent
      });
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to communicate with Aurora Backend',
        loading: false 
      });
    }
  },
  
  setResponse: (r) => set({ response: r, selectedRouteLabel: r.selected_route?.label || null }),
  setError: (e) => set({ error: e }),
  selectRoute: (label) => set({ selectedRouteLabel: label }),
  setTraceExpanded: (v) => set({ traceExpanded: v }),
  reset: () => set({ response: null, error: null, selectedRouteLabel: null, query: '', traceExpanded: false }),
}));
