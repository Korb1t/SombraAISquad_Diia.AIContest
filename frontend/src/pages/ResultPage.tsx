import { ArrowLeft, Copy } from 'lucide-react';
import { useState } from 'react';
import { FeedbackModal } from '@/components/FeedbackModal';

interface ResultPageProps {
  onBack: () => void;
  onFinish: () => void;
  problemText: string;
  // Mock дані - пізніше прийдуть з API
  mockResponse?: {
    serviceName: string;
    phone: string;
    email: string;
    workingHours: string;
  };
}

export function ResultPage({ onBack, onFinish, problemText, mockResponse }: ResultPageProps) {
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackCompleted, setFeedbackCompleted] = useState(false);

  // Mock дані для демо
  const response = mockResponse || {
    serviceName: 'Львівобленерго',
    phone: '(032) 239-21-26',
    email: 'kca@loe.lviv.ua',
    workingHours: 'понеділок-четвер з 8:00 до 17:00, п\'ятниця з 8:00 до 16:00 (обідня перерва з 12:00 до 13:00)',
  };

  const copyToClipboard = (text: string, field: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedField(field);
      setTimeout(() => setCopiedField(null), 2000);
    });
  };

  return (
    <div className="h-full flex flex-col bg-gray-100 overflow-hidden relative">
      {/* Header */}
      <div className="pt-14 pb-4 px-6 bg-white flex-shrink-0">
        <div className="flex items-center gap-4">
          <button 
            onClick={onBack}
            className="w-10 h-10 flex items-center justify-center -ml-2"
          >
            <ArrowLeft className="w-6 h-6 text-gray-900" strokeWidth={2} />
          </button>
          <h1 className="text-xl font-semibold text-gray-900 truncate">
            За місцем проживання
          </h1>
        </div>
      </div>

      {/* Content - БЕЗ скролу */}
      <div className="flex-1 px-6 py-6 flex flex-col overflow-hidden min-h-0">
        {/* Твій запит - БІЛЬША ФОРМА зі скролом тільки тут */}
        <h2 className="text-gray-900 font-semibold text-sm mb-3 flex-shrink-0">
          Твій запит
        </h2>

        <div className="bg-white rounded-2xl p-6 mb-6 shadow-sm relative flex-1 min-h-0 flex flex-col">
          {/* Скролабельний контейнер для тексту */}
          <div className="overflow-y-auto flex-1 pr-10 overscroll-contain">
            <p className="text-gray-700 text-sm leading-relaxed break-words overflow-wrap-anywhere">
              {problemText}
            </p>
          </div>
          
          {/* Кнопка копіювання */}
          <button
            onClick={() => copyToClipboard(problemText, 'request')}
            className="absolute top-5 right-5 w-8 h-8 flex items-center justify-center hover:bg-gray-100 rounded-lg transition-colors flex-shrink-0"
          >
            <Copy className="w-5 h-5 text-gray-600" strokeWidth={2} />
          </button>

          {copiedField === 'request' && (
            <div className="absolute top-5 right-14 bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
              Скопійовано
            </div>
          )}
        </div>

        {/* Рекомендовані служби */}
        <div className="flex-shrink-0">
          <h2 className="text-gray-900 font-semibold text-sm mb-2">
            Рекомендовані служби:
          </h2>
          <p className="text-gray-700 text-sm mb-4">
            {response.serviceName}
          </p>

          {/* Контакти - БЕЗ БІЛИХ РАМОК, менші */}
          <h2 className="text-gray-900 font-semibold text-sm mb-3">
            Контакти:
          </h2>

          {/* Телефон - просто текст */}
          <div className="flex items-center justify-between py-2 mb-1 gap-2">
            <span className="text-gray-700 text-xs break-all">
              {response.phone}
            </span>
            <button
              onClick={() => copyToClipboard(response.phone, 'phone')}
              className="w-7 h-7 flex-shrink-0 flex items-center justify-center hover:bg-gray-200 rounded-lg transition-colors relative"
            >
              <Copy className="w-4 h-4 text-gray-600" strokeWidth={2} />
              {copiedField === 'phone' && (
                <div className="absolute -top-8 right-0 bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                  Скопійовано
                </div>
              )}
            </button>
          </div>

          {/* Email - просто текст */}
          <div className="flex items-center justify-between py-2 mb-1 gap-2">
            <span className="text-gray-700 text-xs break-all">
              {response.email}
            </span>
            <button
              onClick={() => copyToClipboard(response.email, 'email')}
              className="w-7 h-7 flex-shrink-0 flex items-center justify-center hover:bg-gray-200 rounded-lg transition-colors relative"
            >
              <Copy className="w-4 h-4 text-gray-600" strokeWidth={2} />
              {copiedField === 'email' && (
                <div className="absolute -top-8 right-0 bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                  Скопійовано
                </div>
              )}
            </button>
          </div>

          {/* Години роботи - просто текст */}
          <div className="py-2">
            <p className="text-gray-500 text-xs leading-relaxed">
              {response.workingHours}
            </p>
          </div>
        </div>
      </div>

      {/* Кнопка "Завершити" або "На головну" */}
      <div className="flex-shrink-0 px-6 py-4 bg-gray-100">
        <button
          onClick={() => {
            if (feedbackCompleted) {
              onFinish();
            } else {
              setShowFeedback(true);
            }
          }}
          className="w-full bg-black text-white py-4 rounded-2xl font-semibold text-base hover:scale-[1.02] active:scale-[0.98] transition-transform"
        >
          {feedbackCompleted ? 'На головну' : 'Завершити'}
        </button>
      </div>

      {/* Feedback Modal */}
      <FeedbackModal
        isOpen={showFeedback}
        onClose={() => setShowFeedback(false)}
        onComplete={() => {
          setShowFeedback(false);
          setFeedbackCompleted(true);
        }}
      />
    </div>
  );
}

