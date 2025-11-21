import { ArrowLeft, Search, ChevronRight } from 'lucide-react';
import { useState } from 'react';

interface SearchPageProps {
  onBack: () => void;
  onSelect: (address: string) => void;
}

const MOCK_ADDRESSES = [
  'Львівська область, м. Львів, Володимира Великого 10',
  'Львівська область, м. Львів, Володимира Великого 12',
  'Львівська область, м. Львів, Володимира Великого 14',
  'Львівська область, м. Львів, Володимира Великого 16',
  'Львівська область, м. Львів, Наукова 2A',
  'Львівська область, м. Львів, Наукова 5',
];

export function SearchPage({ onBack, onSelect }: SearchPageProps) {
  const [query, setQuery] = useState('');

  const filteredAddresses = query
    ? MOCK_ADDRESSES.filter(addr => 
        addr.toLowerCase().includes(query.toLowerCase())
      )
    : MOCK_ADDRESSES;

  return (
    <div className="h-full flex flex-col bg-gray-100">
      <div className="pt-14 pb-4 px-6 bg-white shadow-sm">
        <div className="flex items-center gap-4 mb-4">
          <button 
            onClick={onBack}
            className="w-10 h-10 flex items-center justify-center -ml-2"
          >
            <ArrowLeft className="w-6 h-6 text-gray-900" strokeWidth={2} />
          </button>
          <h1 className="text-xl font-semibold text-gray-900">
            Шукати
          </h1>
        </div>

        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" strokeWidth={2} />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Володимир"
            className="w-full bg-gray-100 rounded-2xl py-3 pl-12 pr-4 text-base focus:outline-none focus:ring-2 focus:ring-black/10 text-gray-900 placeholder:text-gray-400"
            autoFocus
          />
        </div>
      </div>

      <div className="flex-1 px-4 py-4 overflow-y-auto">
        <div className="bg-white rounded-2xl overflow-hidden shadow-sm">
          {filteredAddresses.map((address, index) => (
            <button
              key={index}
              onClick={() => onSelect(address)}
              className={`w-full px-5 py-4 flex items-center justify-between text-left hover:bg-gray-50 active:bg-gray-100 transition-colors ${
                index !== filteredAddresses.length - 1 ? 'border-b border-gray-100' : ''
              }`}
            >
              <span className="text-sm font-medium text-gray-900 leading-relaxed pr-4">
                {address}
              </span>
              <div className="w-8 h-8 bg-black rounded-full flex items-center justify-center flex-shrink-0">
                <ChevronRight className="w-5 h-5 text-white" strokeWidth={2} />
              </div>
            </button>
          ))}
          
          {filteredAddresses.length === 0 && (
            <div className="p-8 text-center text-gray-500 text-sm">
              Нічого не знайдено
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

