import { useMemo, useRef, useState } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import { ArrowLeft, Plus, Minus, Search, Target, ArrowRight } from 'lucide-react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import tridentImage from '@/assets/trident.png';

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
  onSelectLocation: (payload: { lat: number; lng: number; addressLabel: string }) => void;
}

const mockAddresses = [
  {
    id: 1,
    label: 'Львівська область, м. Львів, Володимира Великого 10',
    coords: [49.8105, 23.981],
  },
  {
    id: 2,
    label: 'Львівська область, м. Львів, Володимира Великого 12',
    coords: [49.811, 23.9822],
  },
  {
    id: 3,
    label: 'Львівська область, м. Львів, Володимира Великого 14',
    coords: [49.8115, 23.9833],
  },
  {
    id: 4,
    label: 'Львівська область, м. Львів, Володимира Великого 16',
    coords: [49.812, 23.9844],
  },
] as const;

async function getAddressFromCoords(lat: number, lng: number): Promise<string> {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&accept-language=uk`
    );
    const data = await response.json();
    
    const addr = data.address;
    const parts = [];
    
    if (addr.state) parts.push(addr.state);
    if (addr.city) parts.push(`м. ${addr.city}`);
    else if (addr.town) parts.push(`м. ${addr.town}`);
    if (addr.road) {
      const street = addr.house_number ? `${addr.road} ${addr.house_number}` : addr.road;
      parts.push(street);
    }
    
    return parts.join(', ') || `Координати: ${lat.toFixed(4)}, ${lng.toFixed(4)}`;
  } catch (error) {
    console.error('Помилка отримання адреси:', error);
    return `Координати: ${lat.toFixed(4)}, ${lng.toFixed(4)}`;
  }
}

function DraggableMarker({
  position,
  setPosition,
  onPositionChange,
}: {
  position: [number, number];
  setPosition: (pos: [number, number]) => void;
  onPositionChange?: (pos: [number, number]) => void;
}) {
  useMapEvents({
    click(e) {
      const newPos: [number, number] = [e.latlng.lat, e.latlng.lng];
      setPosition(newPos);
      onPositionChange?.(newPos);
    },
  });

  return (
    <Marker
      position={position}
      icon={customIcon}
      draggable
      eventHandlers={{
        dragend: (e) => {
          const marker = e.target;
          const position = marker.getLatLng();
          const newPos: [number, number] = [position.lat, position.lng];
          setPosition(newPos);
          onPositionChange?.(newPos);
        },
      }}
    />
  );
}

export function MapPage({ onBack, onSelectLocation }: MapPageProps) {
  const [markerPosition, setMarkerPosition] = useState<[number, number]>([50.4501, 30.5234]);
  const [isLoading, setIsLoading] = useState(false);
  const [showSearchPanel, setShowSearchPanel] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAddressLabel, setSelectedAddressLabel] = useState('');
  const mapRef = useRef<L.Map | null>(null);

  const filteredAddresses = useMemo(() => {
    if (!searchQuery) return mockAddresses;
    return mockAddresses.filter((addr) =>
      addr.label.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [searchQuery]);

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

  const handleSelect = async () => {
    setIsLoading(true);
    
    let label = selectedAddressLabel;
    if (!label) {
      label = await getAddressFromCoords(markerPosition[0], markerPosition[1]);
    }
    
    await new Promise((resolve) => setTimeout(resolve, 1500));
    setIsLoading(false);
    
    onSelectLocation({
      lat: markerPosition[0],
      lng: markerPosition[1],
      addressLabel: label,
    });
  };

  const handleAddressSelect = (address: typeof mockAddresses[number]) => {
    setMarkerPosition([address.coords[0], address.coords[1]]);
    setSelectedAddressLabel(address.label);
    mapRef.current?.flyTo([address.coords[0], address.coords[1]], 17);
    setShowSearchPanel(false);
  };

  return (
    <div className="h-full flex flex-col relative bg-[#e5eef8]">
      <div className="absolute top-0 left-0 right-0 z-[1000] bg-[#dfe8f4]">
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

      {isLoading && (
        <div className="absolute inset-0 top-[60px] z-[1100] bg-gray-100 flex items-center justify-center">
          <div className="animate-pulse">
            <img src={tridentImage} alt="Trident" className="w-16 h-16" />
          </div>
        </div>
      )}

      <div className="flex-1 relative">
        <MapContainer
          center={markerPosition}
          zoom={15}
          style={{ height: '100%', width: '100%' }}
          ref={(map) => {
            if (map) mapRef.current = map;
          }}
          zoomControl={false}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <DraggableMarker
            position={markerPosition}
            setPosition={setMarkerPosition}
            onPositionChange={() => {
              setSelectedAddressLabel('');
            }}
          />
        </MapContainer>

        <div className="absolute top-32 right-4 z-[1000] flex flex-col gap-2.5">
          <button
            onClick={handleZoomIn}
            className="w-11 h-11 bg-black rounded-full flex items-center justify-center shadow-lg hover:scale-105 active:scale-95 transition-transform"
          >
            <Plus className="w-5 h-5 text-white" strokeWidth={2.5} />
          </button>

          <button
            onClick={handleZoomOut}
            className="w-11 h-11 bg-black rounded-full flex items-center justify-center shadow-lg hover:scale-105 active:scale-95 transition-transform"
          >
            <Minus className="w-5 h-5 text-white" strokeWidth={2.5} />
          </button>

          <button
            onClick={() => {
              setShowSearchPanel(true);
              setSearchQuery('');
            }}
            className="w-11 h-11 bg-black rounded-full flex items-center justify-center shadow-lg hover:scale-105 active:scale-95 transition-transform"
          >
            <Search className="w-5 h-5 text-white" strokeWidth={2.5} />
          </button>
        </div>

        <div className="absolute bottom-24 right-4 z-[1000]">
          <button
            onClick={handleMyLocation}
            className="w-12 h-12 bg-black rounded-full flex items-center justify-center shadow-lg hover:scale-105 active:scale-95 transition-transform"
          >
            <Target className="w-6 h-6 text-white" strokeWidth={2.5} />
          </button>
        </div>

        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-[1000]">
          <button
            onClick={handleSelect}
            className="bg-black text-white px-12 py-4 rounded-full font-semibold text-base shadow-xl hover:scale-105 active:scale-95 transition-transform"
          >
            Обрати
          </button>
        </div>
      </div>

      {showSearchPanel && (
        <div className="absolute inset-0 z-[1300] bg-[#e5eef8] flex flex-col">
          <div className="pt-14 pb-4 px-6 flex items-center gap-4">
            <button
              onClick={() => setShowSearchPanel(false)}
              className="w-10 h-10 flex items-center justify-center -ml-2"
            >
              <ArrowLeft className="w-6 h-6 text-gray-900" strokeWidth={2} />
            </button>
            <h1 className="text-xl font-semibold text-gray-900">Шукати</h1>
          </div>

          <div className="px-6">
            <div className="bg-white rounded-2xl flex items-center gap-3 px-4 py-3 shadow-sm">
              <Search className="w-5 h-5 text-gray-400" strokeWidth={2} />
              <input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Володимир"
                className="flex-1 bg-transparent outline-none text-sm"
              />
            </div>
          </div>

          <div className="px-6 mt-4 flex-1 overflow-y-auto">
            <div className="bg-white rounded-3xl shadow-sm p-2 space-y-2">
              {filteredAddresses.map((address) => (
                <button
                  key={address.id}
                  onClick={() => handleAddressSelect(address)}
                  className="w-full flex items-center justify-between px-4 py-3 rounded-2xl hover:bg-gray-100 transition-colors text-left"
                >
                  <span className="text-sm text-gray-800">{address.label}</span>
                  <div className="w-9 h-9 rounded-full bg-black flex items-center justify-center">
                    <ArrowRight className="w-4 h-4 text-white" strokeWidth={2.5} />
                  </div>
                </button>
              ))}
              {!filteredAddresses.length && (
                <p className="text-center text-gray-400 text-sm py-6">Нічого не знайдено</p>
              )}
            </div>
          </div>

          <div className="mt-4 bg-gray-200 rounded-t-[32px] px-10 py-6 text-center text-gray-400 text-sm">
            <div className="h-36 bg-gray-300 rounded-2xl flex items-center justify-center">
              iOS keyboard mock
            </div>
            <button
              onClick={() => setShowSearchPanel(false)}
              className="mt-3 text-sm text-gray-500 underline"
            >
              Приховати
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
