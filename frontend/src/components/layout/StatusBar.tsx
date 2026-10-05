import React, { useEffect, useState } from 'react';
import { useAppStore } from '../../store/useAppStore';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function StatusBar() {
  const [time, setTime] = useState(new Date().toISOString().slice(0, 19) + 'Z');
  const [freshness, setFreshness] = useState<any>(null);

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date().toISOString().slice(0, 19) + 'Z');
    }, 1000);
    return () => clearInterval(timer);
  }, []);
  
  useEffect(() => {
    const fetchHealth = () => {
      axios.get(`${API_URL}/health`).then(res => {
        setFreshness(res.data.data_freshness);
      }).catch(err => console.error("Health check failed", err));
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 60000);
    return () => clearInterval(interval);
  }, []);

  let oldestAge = -1;
  if (freshness) {
    Object.values(freshness).forEach((v: any) => {
      if (v.age_hours > oldestAge) oldestAge = v.age_hours;
    });
  }

  const getFreshnessColor = (age: number) => {
    if (age < 0) return 'text-bridge-dim';
    if (age < 24) return 'text-bridge-success';
    if (age < 72) return 'text-bridge-warning';
    return 'text-bridge-danger';
  };
  
  const freshnessText = oldestAge >= 0 ? `${oldestAge}h (oldest)` : 'N/A';
  const freshnessColor = getFreshnessColor(oldestAge);

  return (
    <div className="h-6 border-t border-bridge-border flex items-center justify-between px-3 bg-bridge-base shrink-0 font-mono text-[10px] text-bridge-faint">
      <div>MODE: ADVISORY · HUMAN APPROVAL REQUIRED</div>
      <div className="flex gap-4">
        <span>DATA FRESHNESS: <span className={freshnessColor}>{freshnessText}</span></span>
        <span>{time}</span>
      </div>
    </div>
  );
}
