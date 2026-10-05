import React, { useEffect, useRef, useState } from 'react';
import * as maplibregl from 'maplibre-gl';
import { useAppStore } from '../../store/useAppStore';
import axios from 'axios';
import type { RouteOption } from '../../api/types';
import DeckGL from '@deck.gl/react';
import { PathLayer, ScatterplotLayer } from '@deck.gl/layers';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ROUTE_COLORS: Record<string, string> = {
  FASTEST: '#C1444A',
  SAFEST: '#4A8B5E',
  BALANCED: '#D49A3A',
  FUEL_EFFICIENT: '#7D8FA3'
};

const STATIONS = [
  { name: 'BHARATI', coords: [76.2, -69.4] },
  { name: 'MAITRI', coords: [11.7, -70.7] }
];

export function PolarMap() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  
  const { response, selectedRouteLabel, loading } = useAppStore();

  // Initialize Map
  useEffect(() => {
    if (map.current) return; // initialize map only once
    
    if (!mapContainer.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {},
        layers: [
          {
            id: 'background',
            type: 'background',
            paint: { 'background-color': '#0A121C' }
          }
        ]
      },
      center: [50, -70], // Between Bharati and Maitri
      zoom: 2.5,
      attributionControl: false
    });

    map.current.on('load', () => {
      setMapLoaded(true);
      
      if (typeof window !== 'undefined') {
        (window as any).__AURORA_MAP__ = map.current;
      }

      // Add Graticule layer
      const graticuleFeatures: any[] = [];
      // Latitudes
      for (let lat = -80; lat <= -60; lat += 10) {
        graticuleFeatures.push({
          type: 'Feature',
          geometry: {
            type: 'LineString',
            coordinates: Array.from({length: 37}, (_, i) => [i * 10 - 180, lat])
          }
        });
      }
      // Longitudes
      for (let lon = -180; lon < 180; lon += 20) {
        graticuleFeatures.push({
          type: 'Feature',
          geometry: {
            type: 'LineString',
            coordinates: [[lon, -90], [lon, -50]]
          }
        });
      }

      map.current!.addSource('graticule', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: graticuleFeatures }
      });

      map.current!.addLayer({
        id: 'graticule-lines',
        type: 'line',
        source: 'graticule',
        paint: {
          'line-color': '#1F3047',
          'line-width': 0.5,
          'line-opacity': 0.5
        }
      });
      
      // Add Station HTML markers
      STATIONS.forEach(s => {
        const el = document.createElement('div');
        el.className = 'flex flex-col items-center pointer-events-none';
        
        const dot = document.createElement('div');
        dot.style.width = '6px';
        dot.style.height = '6px';
        dot.style.backgroundColor = '#FFFFFF';
        dot.style.border = '1px solid #000000';
        
        const label = document.createElement('div');
        label.textContent = s.name;
        label.className = 'text-[10px] text-bridge-text mt-1';
        label.style.fontFamily = 'Inter, system-ui, sans-serif';
        
        el.appendChild(dot);
        el.appendChild(label);
        
        new maplibregl.Marker({ element: el })
          .setLngLat(s.coords as [number, number])
          .addTo(map.current!);
      });
    });

    // Resize observer
    const resizeObserver = new ResizeObserver(() => {
      map.current?.resize();
    });
    resizeObserver.observe(mapContainer.current);

    return () => resizeObserver.disconnect();
  }, []);

  // Sync Data Layers
  useEffect(() => {
    if (!mapLoaded || !map.current) return;
    
    const m = map.current;

    // Clear old dynamic layers
    const clearLayers = () => {
      ['sic-layer', 'icebergs', 'iceberg-cones', 'iceberg-cones-outline'].forEach(id => {
        if (m.getLayer(id)) m.removeLayer(id);
      });
      ['sic-field', 'icebergs', 'iceberg-cones'].forEach(id => {
        if (m.getSource(id)) m.removeSource(id);
      });

      // Clear routes
      m.getStyle().layers.forEach((layer: any) => {
        if (layer.id.startsWith('route-')) {
          m.removeLayer(layer.id);
        }
      });
      Object.keys(m.getStyle().sources).forEach(source => {
        if (source.startsWith('route-')) {
          m.removeSource(source);
        }
      });
    };

    if (!response) {
      clearLayers();
      return;
    }

    clearLayers();

    const drawFeatures = () => {
      // 2. Icebergs (From backend response)
      if (response.icebergs && response.icebergs.length > 0) {
        const icebergFeatures = response.icebergs.map((berg: any) => ({
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [berg.lon, berg.lat] },
          properties: { id: berg.id }
        }));
        if (!m.getSource('icebergs')) {
          m.addSource('icebergs', {
            type: 'geojson',
            data: { type: 'FeatureCollection', features: icebergFeatures as any }
          });
          m.addLayer({
            id: 'icebergs',
            type: 'circle',
            source: 'icebergs',
            paint: {
              'circle-radius': 6,
              'circle-color': '#D49A3A',
              'circle-stroke-width': 1,
              'circle-stroke-color': '#0A121C'
            }
          });
        }
        
        const envelopeFeatures = response.icebergs
          .filter((berg: any) => berg.envelope)
          .map((berg: any) => ({
            type: 'Feature',
            geometry: berg.envelope,
            properties: {}
          }));
          
        if (envelopeFeatures.length > 0 && !m.getSource('iceberg-cones')) {
          m.addSource('iceberg-cones', {
            type: 'geojson',
            data: { type: 'FeatureCollection', features: envelopeFeatures as any }
          });
          m.addLayer({
            id: 'iceberg-cones',
            type: 'fill',
            source: 'iceberg-cones',
            paint: {
              'fill-color': '#D49A3A',
              'fill-opacity': 0.15,
            }
          }, 'icebergs'); // insert before icebergs so cones are below points
          
          m.addLayer({
            id: 'iceberg-cones-outline',
            type: 'line',
            source: 'iceberg-cones',
            paint: {
              'line-color': '#D49A3A',
              'line-width': 0.5,
              'line-opacity': 0.4
            }
          }, 'icebergs');
        }
      }

      // 3. Routes
      const routes = [...(response.routes || [])].reverse();
      routes.forEach(route => {
        const isSelected = route.label === selectedRouteLabel;
        
        const geojson = {
          type: 'Feature',
          geometry: {
            type: 'LineString',
            // Backend coords are [lat, lon], maplibre needs [lon, lat]
            coordinates: route.geometry.map(p => [p[1], p[0]])
          }
        };

        if (!m.getSource(`route-${route.label}`)) {
          m.addSource(`route-${route.label}`, {
            type: 'geojson',
            data: geojson as any
          });

          if (isSelected) {
            m.addLayer({
              id: `route-${route.label}-outline`,
              type: 'line',
              source: `route-${route.label}`,
              layout: { 'line-join': 'round', 'line-cap': 'round' },
              paint: {
                'line-color': '#0A121C',
                'line-width': 6,
                'line-opacity': 0.6
              }
            });
          }

          m.addLayer({
            id: `route-${route.label}`,
            type: 'line',
            source: `route-${route.label}`,
            layout: { 'line-join': 'round', 'line-cap': 'round' },
            paint: {
              'line-color': isSelected ? '#FFFFFF' : (ROUTE_COLORS[route.label] || '#7D8FA3'),
              'line-width': isSelected ? 8 : 4,
              'line-opacity': 1.0
            }
          });
        }
      });
      
      // Auto-fit bounds if we have routes
      if (routes.length > 0) {
        let minLon = 180, maxLon = -180, minLat = 90, maxLat = -90;
        routes.forEach(r => {
          r.geometry.forEach(p => {
            const lat = p[0], lon = p[1];
            if (lon < minLon) minLon = lon;
            if (lon > maxLon) maxLon = lon;
            if (lat < minLat) minLat = lat;
            if (lat > maxLat) maxLat = lat;
          });
        });
        if (minLon !== 180) {
          m.fitBounds([[minLon, minLat], [maxLon, maxLat]], { padding: 50, duration: 1000 });
        }
      }
    };

    // 1. Fetch and add SIC
    axios.get(`${API_URL}/map/sic-field`).then(res => {
      const data = res.data;
      if (!m.getSource('sic-field')) {
        m.addSource('sic-field', {
          type: 'image',
          url: data.image_base64,
          coordinates: [
            [data.bounds.west, data.bounds.north],
            [data.bounds.east, data.bounds.north],
            [data.bounds.east, data.bounds.south],
            [data.bounds.west, data.bounds.south]
          ]
        });

        m.addLayer({
          id: 'sic-layer',
          type: 'raster',
          source: 'sic-field',
          paint: { 'raster-opacity': 0.7, 'raster-fade-duration': 300 }
        });
      }
      drawFeatures();
    }).catch(err => {
      console.error("Failed to load SIC field", err);
      drawFeatures();
    });

  }, [response, mapLoaded]);

  // Handle Selection updates (restyling)
  useEffect(() => {
    if (!map.current || !response || !mapLoaded) return;
    const m = map.current;
    
    response.routes.forEach(route => {
      const isSelected = route.label === selectedRouteLabel;
      if (!m.getSource(`route-${route.label}`)) return;
      if (m.getLayer(`route-${route.label}`)) {
        m.setPaintProperty(`route-${route.label}`, 'line-color', isSelected ? '#FFFFFF' : (ROUTE_COLORS[route.label] || '#7D8FA3'));
        m.setPaintProperty(`route-${route.label}`, 'line-width', isSelected ? 4 : 2);
        m.setPaintProperty(`route-${route.label}`, 'line-opacity', isSelected ? 1.0 : 0.5);
      }
      
      const outlineId = `route-${route.label}-outline`;
      if (isSelected && !m.getLayer(outlineId)) {
        m.addLayer({
          id: outlineId,
          type: 'line',
          source: `route-${route.label}`,
          layout: { 'line-join': 'round', 'line-cap': 'round' },
          paint: {
            'line-color': '#0A121C',
            'line-width': 6,
            'line-opacity': 0.6
          }
        }, `route-${route.label}`);
      } else if (!isSelected && m.getLayer(outlineId)) {
        m.removeLayer(outlineId);
      }
    });

  }, [selectedRouteLabel, response, mapLoaded]);

  // Map Controls
  const handleZoom = (delta: number) => map.current?.zoomTo(map.current.getZoom() + delta);
  const handleReset = () => map.current?.flyTo({ center: [50, -70], zoom: 2.5 });

  const deckLayers = [];
  if (response) {
    deckLayers.push(
      new PathLayer({
        id: 'deck-routes',
        data: response.routes,
        getPath: (d: any) => d.geometry.map((p: any) => [p[1], p[0]]),
        getColor: (d: any) => {
          if (d.label === selectedRouteLabel) return [255, 255, 255, 255];
          if (d.label === 'FASTEST') return [193, 68, 74, 255];
          if (d.label === 'SAFEST') return [74, 139, 94, 255];
          if (d.label === 'BALANCED') return [212, 154, 58, 255];
          return [125, 143, 163, 255];
        },
        getWidth: (d: any) => (d.label === selectedRouteLabel ? 6 : 3),
        widthUnits: 'pixels',
      }) as any
    );
    deckLayers.push(
      new ScatterplotLayer({
        id: 'deck-icebergs',
        data: response.icebergs || [],
        getPosition: (d: any) => [d.lon, d.lat],
        getFillColor: [212, 154, 58, 255],
        getRadius: 8,
        radiusUnits: 'pixels',
        radiusMinPixels: 6,
      }) as any
    );
  }

  return (
    <div className="panel h-full flex flex-col border-r-0 border-l-0 relative">
      <div className="panel-header absolute top-0 left-0 right-0 z-10 bg-bridge-base/80 backdrop-blur-none border-b border-bridge-border">
        POLAR VIEW
      </div>
      
      {/* Map Container */}
      <div className="flex-1 w-full h-full relative" id="maplibre-wrapper">
        <div ref={mapContainer} className="w-full h-full bg-bridge-deep" id="map-container" />
        <div className="absolute inset-0 pointer-events-none z-[40]">
          <DeckGL
            initialViewState={{
              longitude: 44,
              latitude: -70,
              zoom: 2.5,
              pitch: 0,
              bearing: 0,
            }}
            controller={false}
            layers={deckLayers}
          />
        </div>
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 z-20 flex items-center justify-center bg-bridge-deep/60">
          <div className="text-bridge-text text-[11px] mono animate-pulse tracking-widest bg-bridge-base px-3 py-1 border border-bridge-border">
            COMPUTING ROUTES...
          </div>
        </div>
      )}

      {/* Custom Controls */}
      <div className="absolute top-10 right-4 z-10 flex flex-col gap-1">
        <button onClick={() => handleZoom(1)} className="w-6 h-6 flex items-center justify-center border border-bridge-border bg-bridge-surface text-bridge-text hover:bg-bridge-muted transition-colors leading-none pb-0.5">+</button>
        <button onClick={() => handleZoom(-1)} className="w-6 h-6 flex items-center justify-center border border-bridge-border bg-bridge-surface text-bridge-text hover:bg-bridge-muted transition-colors leading-none pb-0.5">-</button>
        <button onClick={handleReset} className="w-6 h-6 flex items-center justify-center border border-bridge-border bg-bridge-surface text-bridge-text hover:bg-bridge-muted transition-colors text-[10px]">⌂</button>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 right-4 z-10 bg-bridge-surface/90 border border-bridge-border px-2 py-1.5 text-[10px] mono">
        <div className="font-sans font-medium text-bridge-dim mb-1 uppercase tracking-wider">LEGEND</div>
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2"><div className="w-3 h-1" style={{backgroundColor: ROUTE_COLORS.FASTEST}} /> FASTEST</div>
          <div className="flex items-center gap-2"><div className="w-3 h-1" style={{backgroundColor: ROUTE_COLORS.SAFEST}} /> SAFEST</div>
          <div className="flex items-center gap-2"><div className="w-3 h-1" style={{backgroundColor: ROUTE_COLORS.BALANCED}} /> BALANCED</div>
          <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full border border-bridge-deep bg-bridge-warning ml-0.5" /> Iceberg</div>
          <div className="flex items-center gap-2"><div className="w-2 h-2 border border-black bg-white ml-0.5" /> Station</div>
        </div>
      </div>
      
      {/* Scale Bar */}
      <div className="absolute bottom-4 left-4 z-10 text-[10px] mono text-bridge-faint">
        Scale ~ 1:10M (Equatorial)
      </div>
    </div>
  );
}
