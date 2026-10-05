export const fmt = {
  km: (v: number) => `${v.toFixed(1)} km`,
  hours: (v: number) => `${v.toFixed(1)} h`,
  tonnes: (v: number) => `${v.toFixed(1)} t`,
  risk: (v: number) => v.toFixed(3),
  percent: (v: number) => `${Math.round(v * 100)}%`,
  coord: (v: number, axis: 'lat' | 'lon') => {
    const dir = axis === 'lat' ? (v < 0 ? 'S' : 'N') : (v < 0 ? 'W' : 'E');
    return `${Math.abs(v).toFixed(4)}°${dir}`;
  },
  duration: (ms: number) => {
    if (ms < 1) return `${ms.toFixed(1)}ms`;
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  }
};
