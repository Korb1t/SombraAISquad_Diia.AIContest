import tridentImage from '@/assets/trident.png';

export function Loader() {
  return (
    <div className="flex items-center justify-center h-full bg-gray-100">
      <div className="animate-pulse">
          <img src={tridentImage} alt="Trident" className="w-20 h-20" />
      </div>
    </div>
  );
}

