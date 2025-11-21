import { useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import { ArrowLeft, Plus, Minus, Search, Target } from 'lucide-react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Створюємо кастомну іконку для маркера (червона шпилька)
const customIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" width="40" height="55" viewBox="0 0 40 55">
      <g>
        <path d="M20 0C9 0 0 9 0 20c0 15 20 35 20 35s20-20 20-35C40 9 31 0 20 0z" 
              fill="#DC2626" stroke="#991B1B" stroke-width="2"/>
        <circle cx="20" cy="20" r="8" fill="white"/>
      </g>
    </svg>
  `),
  iconSize: [40, 55],
  iconAnchor: [20, 55],
  popupAnchor: [0, -55],
});

interface MapPageProps {
  onBack: () => void;
  onSelectLocation: (lat: number, lng: number) => void;
}

// Компонент для переміщення маркера при кліку
function DraggableMarker({ 
  position, 
  setPosition 
}: { 
  position: [number, number]; 
  setPosition: (pos: [number, number]) => void;
}) {
  useMapEvents({
    click(e) {
      setPosition([e.latlng.lat, e.latlng.lng]);
    },
  });

  return (
    <Marker 
      position={position} 
      icon={customIcon}
      draggable={true}
      eventHandlers={{
        dragend: (e) => {
          const marker = e.target;
          const position = marker.getLatLng();
          setPosition([position.lat, position.lng]);
        },
      }}
    />
  );
}

export function MapPage({ onBack, onSelectLocation }: MapPageProps) {
  // Київ - дефолтна позиція
  const [markerPosition, setMarkerPosition] = useState<[number, number]>([50.4501, 30.5234]);
  const mapRef = useRef<L.Map | null>(null);

  const handleZoomIn = () => {
    if (mapRef.current) {
      mapRef.current.zoomIn();
    }
  };

  const handleZoomOut = () => {
    if (mapRef.current) {
      mapRef.current.zoomOut();
    }
  };

  const handleMyLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const newPos: [number, number] = [
            position.coords.latitude,
            position.coords.longitude,
          ];
          setMarkerPosition(newPos);
          if (mapRef.current) {
            mapRef.current.flyTo(newPos, 15);
          }
        },
        (error) => {
          console.error('Помилка отримання геолокації:', error);
        }
      );
    }
  };

  const handleSelect = () => {
    onSelectLocation(markerPosition[0], markerPosition[1]);
  };

  return (
    <div className="h-full flex flex-col relative">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-[1000] bg-white/95 backdrop-blur-sm shadow-sm">
        <div className="pt-14 pb-4 px-6">
          <div className="flex items-center gap-4">
            <button 
              onClick={onBack}
              className="w-10 h-10 flex items-center justify-center -ml-2"
            >
              <ArrowLeft className="w-6 h-6 text-gray-900" strokeWidth={2} />
            </button>
            <h1 className="text-xl font-semibold text-gray-900">
              Інша адреса
            </h1>
          </div>
        </div>
      </div>

      {/* Карта */}
      <div className="flex-1 relative">
        <MapContainer
          center={markerPosition}
          zoom={15}
          style={{ height: '100%', width: '100%' }}
          ref={mapRef}
          zoomControl={false}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <DraggableMarker position={markerPosition} setPosition={setMarkerPosition} />
        </MapContainer>

        {/* Кнопки управління справа */}
        <div className="absolute top-24 right-4 z-[1000] flex flex-col gap-3">
          {/* Zoom In */}
          <button
            onClick={handleZoomIn}
            className="w-12 h-12 bg-black rounded-full flex items-center justify-center shadow-lg hover:scale-105 active:scale-95 transition-transform"
          >
            <Plus className="w-6 h-6 text-white" strokeWidth={2.5} />
          </button>

          {/* Zoom Out */}
          <button
            onClick={handleZoomOut}
            className="w-12 h-12 bg-black rounded-full flex items-center justify-center shadow-lg hover:scale-105 active:scale-95 transition-transform"
          >
            <Minus className="w-6 h-6 text-white" strokeWidth={2.5} />
          </button>

          {/* Search (поки неактивна) */}
          <button
            disabled
            className="w-12 h-12 bg-black rounded-full flex items-center justify-center shadow-lg opacity-50"
          >
            <Search className="w-6 h-6 text-white" strokeWidth={2.5} />
          </button>
        </div>

        {/* Кнопка "Моя локація" внизу справа */}
        <div className="absolute bottom-24 right-4 z-[1000]">
          <button
            onClick={handleMyLocation}
            className="w-14 h-14 bg-black rounded-full flex items-center justify-center shadow-lg hover:scale-105 active:scale-95 transition-transform"
          >
            <Target className="w-7 h-7 text-white" strokeWidth={2.5} />
          </button>
        </div>

        {/* Кнопка "Обрати" */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-[1000]">
          <button
            onClick={handleSelect}
            className="bg-black text-white px-12 py-4 rounded-full font-semibold text-base shadow-xl hover:scale-105 active:scale-95 transition-transform"
          >
            Обрати
          </button>
        </div>
      </div>
    </div>
  );
}



