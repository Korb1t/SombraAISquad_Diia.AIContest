import { Search, Newspaper, FileText, Zap, User } from 'lucide-react';

interface ServiceCardProps {
  title: string;
  icon?: React.ReactNode;
  isBlurred?: boolean;
  onClick?: () => void;
}

function ServiceCard({ title, icon, isBlurred = false, onClick }: ServiceCardProps) {
  return (
    <button
      onClick={onClick}
      disabled={isBlurred}
      className={`
        relative bg-white/70 backdrop-blur-sm rounded-2xl p-4 h-32
        shadow-sm transition-all duration-200
        ${isBlurred ? 'opacity-40 blur-sm cursor-default' : 'hover:scale-105 active:scale-95'}
      `}
    >
      <div className="flex flex-col items-start h-full">
        <div className="w-10 h-10 bg-black rounded-full flex items-center justify-center mb-3">
          {icon || <div className="w-5 h-5 bg-white rounded-full" />}
        </div>
        
        <div className="text-left">
          <p className="text-sm font-medium text-gray-900 leading-tight">
            {title}
          </p>
        </div>
      </div>
    </button>
  );
}

interface HomePageProps {
  onNavigateToClassifier: () => void;
}

export function HomePage({ onNavigateToClassifier }: HomePageProps) {
  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-blue-100 via-cyan-50 to-yellow-50">
      <div className="pt-16 pb-4 px-6 bg-transparent">
        <h1 className="text-3xl font-bold text-gray-900">
          Сервіси
        </h1>
      </div>

      <div className="px-6 mb-4">
        <div className="bg-white/80 backdrop-blur-md rounded-2xl px-4 py-3 flex items-center gap-3 shadow-sm">
          <Search className="w-5 h-5 text-gray-400" strokeWidth={2} />
          <span className="text-gray-400 text-[15px]">Пошук</span>
        </div>
      </div>

      <div className="flex-1 px-6 pb-20 overflow-y-auto">
        <div className="grid grid-cols-2 gap-3">
          <ServiceCard title="Військовий облік" isBlurred />
          <ServiceCard title="Перевірити довіреність" isBlurred />
          <ServiceCard title="Допомога бізнесу" isBlurred />
          
          <ServiceCard 
            title="Комунальні Проблеми"
            icon={<div className="w-3 h-3 bg-white rounded-full" />}
            onClick={onNavigateToClassifier}
          />
          
          <ServiceCard title="Штрафи та заборгованість" isBlurred />
          <ServiceCard title="Підтримка підприємців" isBlurred />
          <ServiceCard title="Гаряча лінія" isBlurred />
          <ServiceCard title="Соціальні виплати" isBlurred />
          <ServiceCard title="ЄПідтримка" isBlurred />
          <ServiceCard title="Ветеранська підтримка" isBlurred />
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 bg-white/95 backdrop-blur-xl border-t border-gray-200">
        <div className="flex items-center justify-around px-4 py-2 pb-3">
          <button className="flex flex-col items-center gap-1 py-1 px-4">
            <Newspaper className="w-6 h-6 text-gray-400" strokeWidth={2} />
            <span className="text-[11px] text-gray-400 font-medium">Стрічка</span>
          </button>

          <button className="flex flex-col items-center gap-1 py-1 px-4">
            <FileText className="w-6 h-6 text-gray-400" strokeWidth={2} />
            <span className="text-[11px] text-gray-400 font-medium">Документи</span>
          </button>

          <button className="flex flex-col items-center gap-1 py-1 px-4">
            <Zap className="w-6 h-6 text-gray-900" strokeWidth={2} fill="currentColor" />
            <span className="text-[11px] text-gray-900 font-semibold">Сервіси</span>
          </button>

          <button className="flex flex-col items-center gap-1 py-1 px-4">
            <User className="w-6 h-6 text-gray-400" strokeWidth={2} />
            <span className="text-[11px] text-gray-400 font-medium">Меню</span>
          </button>
        </div>
      </div>
    </div>
  );
}

