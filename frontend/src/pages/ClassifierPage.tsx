import { ArrowLeft, ArrowRight } from 'lucide-react';

interface ClassifierPageProps {
  onBack: () => void;
  onSelectLocation: (type: 'current' | 'other') => void;
}

export function ClassifierPage({ onBack, onSelectLocation }: ClassifierPageProps) {
  return (
    <div className="h-full flex flex-col bg-gray-100">
      <div className="pt-14 pb-4 px-6 bg-white">
        <div className="flex items-center gap-4">
          <button 
            onClick={onBack}
            className="w-10 h-10 flex items-center justify-center -ml-2"
          >
            <ArrowLeft className="w-6 h-6 text-gray-900" strokeWidth={2} />
          </button>
          <h1 className="text-xl font-semibold text-gray-900">
            Комунальні Проблеми
          </h1>
        </div>
      </div>

      <div className="flex-1 px-6 py-6 overflow-y-auto">
        <p className="text-gray-700 text-base leading-relaxed mb-6">
          Виявили несправності в освітленні, водопостачанні чи опаленні у своєму будинку? 
          Або зафіксували неправильно припаркований автомобіль і не знаєте, до якої служби 
          звернутися?
        </p>

        <div className="bg-gradient-to-br from-purple-50 via-blue-50 to-cyan-50 border-2 border-purple-200 rounded-2xl p-4 mb-8">
          <div className="flex gap-3">
            <div className="text-3xl flex-shrink-0">
              👆
            </div>
            <p className="text-gray-800 text-sm leading-relaxed">
              Ми допоможемо тобі коректно сформувати запит та підкажемо відповідальні служби
            </p>
          </div>
        </div>

        <h2 className="text-gray-900 font-semibold text-base mb-4">
          Визнач локацію проблеми
        </h2>

        <button
          onClick={() => onSelectLocation('current')}
          className="w-full bg-white rounded-2xl px-5 py-4 mb-3 flex items-center justify-between shadow-sm hover:shadow-md transition-shadow active:scale-98"
        >
          <span className="text-gray-900 font-medium text-[15px]">
            За місцем проживання
          </span>
          <div className="w-10 h-10 bg-black rounded-full flex items-center justify-center flex-shrink-0">
            <ArrowRight className="w-5 h-5 text-white" strokeWidth={2.5} />
          </div>
        </button>

        <button
          onClick={() => onSelectLocation('other')}
          className="w-full bg-white rounded-2xl px-5 py-4 flex items-center justify-between shadow-sm hover:shadow-md transition-shadow active:scale-98"
        >
          <span className="text-gray-900 font-medium text-[15px]">
            Інша адреса
          </span>
          <div className="w-10 h-10 bg-black rounded-full flex items-center justify-center flex-shrink-0">
            <ArrowRight className="w-5 h-5 text-white" strokeWidth={2.5} />
          </div>
        </button>
      </div>
    </div>
  );
}

