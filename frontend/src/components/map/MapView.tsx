import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Location } from '../../types';

interface MapViewProps {
    center: Location;
    markers?: Array<{
        position: Location;
        label: string;
        color?: 'blue' | 'red' | 'green' | 'orange';
    }>;
    zoom?: number;
    height?: string;
}

const MapView: React.FC<MapViewProps> = ({
    center,
    markers = [],
    zoom = 13,
    height = '400px',
}) => {
    const mapRef = useRef<L.Map | null>(null);
    const mapContainerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!mapContainerRef.current || mapRef.current) return;

        // Initialize map
        const map = L.map(mapContainerRef.current).setView(
            [center.latitude, center.longitude],
            zoom
        );

        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        }).addTo(map);

        mapRef.current = map;

        return () => {
            map.remove();
            mapRef.current = null;
        };
    }, []);

    useEffect(() => {
        if (!mapRef.current) return;

        // Update center
        mapRef.current.setView([center.latitude, center.longitude], zoom);
    }, [center, zoom]);

    useEffect(() => {
        if (!mapRef.current) return;

        // Clear existing markers
        mapRef.current.eachLayer((layer) => {
            if (layer instanceof L.Marker) {
                layer.remove();
            }
        });

        // Add new markers
        markers.forEach((marker) => {
            const icon = L.divIcon({
                className: 'custom-marker',
                html: `
          <div class="relative">
            <div class="absolute -translate-x-1/2 -translate-y-full">
              <div class="bg-${marker.color || 'blue'}-500 text-white rounded-full h-8 w-8 flex items-center justify-center shadow-lg">
                <span class="text-xs font-bold">${marker.label.charAt(0)}</span>
              </div>
              <div class="absolute left-1/2 -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-${marker.color || 'blue'}-500"></div>
            </div>
          </div>
        `,
                iconSize: [32, 32],
                iconAnchor: [16, 32],
            });

            L.marker([marker.position.latitude, marker.position.longitude], { icon })
                .bindPopup(marker.label)
                .addTo(mapRef.current!);
        });
    }, [markers]);

    return (
        <div
            ref={mapContainerRef}
            style={{ height, width: '100%' }}
            className="rounded-lg shadow-md"
        />
    );
};

export default MapView;
