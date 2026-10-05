import axios from 'axios';
import type { AnalysisResponse } from './types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_URL,
  timeout: 120000,
});

export async function analyze(query: string): Promise<AnalysisResponse> {
  const { data } = await client.post<AnalysisResponse>('/analyze', { query });
  return data;
}

export async function health() {
  const { data } = await client.get('/health');
  return data;
}
