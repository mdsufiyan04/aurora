import re

with open('c:/Users/mdsuf/OneDrive/Desktop/26059/frontend/src/components/map/PolarMap.tsx', 'r') as f:
    code = f.read()

replacement = """    const drawFeatures = () => {
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
              'line-width': isSelected ? 4 : 2,
              'line-opacity': isSelected ? 1.0 : 0.5,
              'line-dasharray': isSelected ? undefined : [2, 2]
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
"""

import re
start_idx = code.find("    // 1. Fetch and add SIC")
end_idx = code.find("  }, [response, mapLoaded]);", start_idx)

if start_idx != -1 and end_idx != -1:
    new_code = code[:start_idx] + replacement + "\n" + code[end_idx:]
    with open('c:/Users/mdsuf/OneDrive/Desktop/26059/frontend/src/components/map/PolarMap.tsx', 'w') as f:
        f.write(new_code)
    print("SUCCESS")
else:
    print("FAILED TO FIND")
