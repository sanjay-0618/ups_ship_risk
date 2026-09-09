import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Polyline, CircleMarker, Popup, Marker } from 'react-leaflet';
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
import type { RouteResult, Shipment, WeatherEvent } from '../../types';

// Fix Leaflet icon issue in React
let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});
L.Marker.prototype.options.icon = DefaultIcon;

interface LogisticsMapProps {
  center?: [number, number];
  zoom?: number;
  routes?: RouteResult[];
  selectedRouteId?: string;
  shipments?: Shipment[];
  weatherEvents?: WeatherEvent[];
  showRoutes?: boolean;
  showShipments?: boolean;
  showWeather?: boolean;
  height?: string;
  onShipmentClick?: (shipment: Shipment) => void;
  onRouteClick?: (routeId: string) => void;
}

const riskColors = {
  LOW: '#22c55e',
  MEDIUM: '#eab308',
  HIGH: '#f97316',
  CRITICAL: '#ef4444'
};

export default function LogisticsMap({
  center = [39.8283, -98.5795], // US center
  zoom = 4,
  routes = [],
  selectedRouteId,
  shipments = [],
  weatherEvents = [],
  showRoutes = true,
  showShipments = true,
  showWeather = true,
  height = '400px',
  onShipmentClick,
  onRouteClick
}: LogisticsMapProps) {
  
  return (
    <div style={{ height, width: '100%', borderRadius: '0.75rem', overflow: 'hidden' }}>
      <MapContainer center={center} zoom={zoom} scrollWheelZoom={true} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {showRoutes && routes.map(route => {
          const isSelected = route.route_id === selectedRouteId;
          const color = riskColors[route.risk_level] || '#3b82f6';
          // Convert waypoints to LatLng expressions for Polyline
          const positions: [number, number][] = route.waypoints.map(w => [w.latitude, w.longitude]);
          
          return (
            <Polyline
              key={route.route_id}
              positions={positions}
              pathOptions={{
                color,
                weight: isSelected ? 6 : 3,
                opacity: isSelected ? 1 : 0.6,
                dashArray: isSelected ? undefined : '10, 10'
              }}
              eventHandlers={{
                click: () => onRouteClick && onRouteClick(route.route_id)
              }}
            />
          );
        })}

        {showShipments && shipments.map(shipment => {
          // Assuming shipment has lat/lng or we map from current location
          // For simplicity, we might not have lat/lng in shipment directly without joining.
          // Let's assume they are injected or we just skip if missing
          return null; // Implementation depends on full data structure
        })}
      </MapContainer>
    </div>
  );
}
