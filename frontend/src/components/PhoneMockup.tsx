import { ReactNode, useState, useEffect } from 'react';
import { Wifi, Signal, Battery } from 'lucide-react';
import { cn } from '@/lib/utils';

interface PhoneMockupProps {
  children: ReactNode;
  className?: string;
}

/**
 * Мокап iPhone для демонстрації додатку
 * Весь контент рендериться всередині цього компонента
 */
export function PhoneMockup({ children, className }: PhoneMockupProps) {
  // Реальний час
  const [time, setTime] = useState('');

  useEffect(() => {
    // Оновлюємо час кожну секунду
    const updateTime = () => {
      const now = new Date();
      const hours = now.getHours().toString().padStart(2, '0');
      const minutes = now.getMinutes().toString().padStart(2, '0');
      setTime(`${hours}:${minutes}`);
    };

    updateTime(); // Відразу показуємо час
    const interval = setInterval(updateTime, 1000); // Оновлюємо кожну секунду

    return () => clearInterval(interval);
  }, []);

  return (
    <div className={cn("relative mx-auto w-full max-w-[400px]", className)}>
      {/* iPhone 15 Pro корпус - 393x852px */}
      <div className="relative bg-black rounded-[3.5rem] p-3 shadow-2xl w-full aspect-[393/852] max-h-[calc(100vh-4rem)]">
        {/* Відблиск на рамці (реалістичність) */}
        <div className="absolute inset-0 rounded-[3.5rem] bg-gradient-to-br from-gray-700 via-black to-gray-900 opacity-50" />
        
        {/* Кнопки на боці */}
        <div className="absolute -left-1 top-24 w-1 h-8 bg-gray-800 rounded-l" />
        <div className="absolute -left-1 top-36 w-1 h-12 bg-gray-800 rounded-l" />
        <div className="absolute -left-1 top-52 w-1 h-12 bg-gray-800 rounded-l" />
        <div className="absolute -right-1 top-36 w-1 h-16 bg-gray-800 rounded-r" />
        
        {/* Dynamic Island */}
        <div className="absolute top-2 left-1/2 -translate-x-1/2 w-28 h-7 bg-black rounded-full z-[10000] shadow-lg pointer-events-none" />
        
        {/* Екран айфону */}
        <div className="relative w-full h-full bg-white rounded-[3rem] overflow-hidden shadow-inner">
          {/* Контент додатку */}
          <div className="absolute inset-0 overflow-y-auto">
            {children}
          </div>

          {/* Status bar (час, батарея, сигнал) - ПОВЕРХ контенту */}
          <div className="absolute top-0 left-0 right-0 h-14 z-[9999] px-8 pt-2.5 pointer-events-none">
            <div className="flex items-center justify-between text-[15px] font-semibold">
              <span className="text-gray-900">{time || '00:00'}</span>
              <div className="w-24" /> {/* Пропуск для Dynamic Island */}
              <div className="flex items-center gap-1.5 text-gray-900">
                {/* Сигнал - lucide icon */}
                <Signal className="w-4 h-4" strokeWidth={2.5} />
                {/* WiFi - lucide icon */}
                <Wifi className="w-4 h-4" strokeWidth={2.5} />
                {/* Батарея - lucide icon */}
                <Battery className="w-5 h-4" strokeWidth={2.5} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

