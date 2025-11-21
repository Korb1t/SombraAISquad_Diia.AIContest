import { useState } from 'react';
import { X, Check } from 'lucide-react';

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
}

type Emoji = '😠' | '😐' | '😕' | '😁';

const feedbackOptions = [
  { id: 'accessible', label: 'Доступний процес' },
  { id: 'understandable', label: 'Зрозумілий процес' },
  { id: 'fast', label: 'Швидке формування' },
  { id: 'useful', label: 'Корисна функція' },
  { id: 'other', label: 'Інше' },
];

export function FeedbackModal({ isOpen, onClose, onComplete }: FeedbackModalProps) {
  const [step, setStep] = useState<'form' | 'thanks'>('form');
  const [selectedEmoji, setSelectedEmoji] = useState<Emoji | null>(null);
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  const [comment, setComment] = useState('');

  const handleEmojiSelect = (emoji: Emoji) => {
    setSelectedEmoji(emoji);
  };

  const toggleOption = (optionId: string) => {
    setSelectedOptions(prev =>
      prev.includes(optionId)
        ? prev.filter(id => id !== optionId)
        : [...prev, optionId]
    );
  };

  const handleSubmit = () => {
    console.log('Feedback:', { selectedEmoji, selectedOptions, comment });
    setStep('thanks');
  };

  const handleClose = () => {
    onClose();
    setTimeout(() => {
      setStep('form');
      setSelectedEmoji(null);
      setSelectedOptions([]);
      setComment('');
    }, 300);
  };

  const handleThankYouClose = () => {
    handleClose();
    onComplete();
  };

  if (!isOpen) return null;

  return (
    <>
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm z-50 transition-opacity duration-300"
        onClick={step === 'thanks' ? handleThankYouClose : handleClose}
      />

      {step === 'form' ? (
        <div
          className={`absolute bottom-0 left-0 right-0 z-50 transition-transform duration-500 ease-out ${
            isOpen ? 'translate-y-0' : 'translate-y-full'
          }`}
        >
          <div className="bg-white rounded-t-3xl shadow-2xl overflow-hidden">
            <div>
              <div className="bg-white px-6 pt-6 pb-4 border-b border-gray-200 flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-900">
                  Поділіться враженнями
                </h2>
                <button
                  onClick={handleClose}
                  className="w-8 h-8 flex items-center justify-center hover:bg-gray-100 rounded-full transition-colors"
                >
                  <X className="w-5 h-5 text-gray-600" strokeWidth={2} />
                </button>
              </div>

              <div className="px-6 py-4">
                <p className="text-gray-700 text-sm mb-5 leading-relaxed">
                  Задоволені формуванням запитом по Комунальним Проблемам в Diï?
                </p>

                <div className="flex gap-3 justify-center mb-6">
                  {(['😠', '😐', '😕', '😁'] as Emoji[]).map((emoji) => (
                    <button
                      key={emoji}
                      onClick={() => handleEmojiSelect(emoji)}
                      className="relative w-14 h-14 text-4xl hover:scale-110 transition-all"
                    >
                      <span className={selectedEmoji === emoji ? 'grayscale' : ''}>
                        {emoji}
                      </span>
                      {selectedEmoji === emoji && (
                        <div className="absolute -top-1 -right-1 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                          <Check className="w-4 h-4 text-white" strokeWidth={3} />
                        </div>
                      )}
                    </button>
                  ))}
                </div>

                <div className="mb-5">
                  <h3 className="text-gray-900 font-semibold text-sm mb-2">
                    Що сподобалось?
                  </h3>
                  <p className="text-gray-400 text-xs mb-3">
                    Оберіть один або кілька варіантів.
                  </p>

                  <div className="flex flex-wrap gap-2">
                    {feedbackOptions.map((option) => (
                      <button
                        key={option.id}
                        onClick={() => toggleOption(option.id)}
                        className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                          selectedOptions.includes(option.id)
                            ? 'bg-gray-900 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="mb-5">
                  <h3 className="text-gray-900 font-semibold text-sm mb-2">
                    Як можна покращити послугу?
                  </h3>
                  <p className="text-gray-400 text-xs mb-2">
                    Розкажіть більше про враження (необов'язково)
                  </p>

                  <textarea
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    placeholder="Ваш коментар..."
                    className="w-full h-20 px-4 py-3 text-sm border border-gray-300 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                  />
                </div>

                <button
                  onClick={handleSubmit}
                  disabled={!selectedEmoji}
                  className={`w-full py-4 rounded-2xl font-semibold text-base transition-all ${
                    selectedEmoji
                      ? 'bg-black text-white hover:scale-[1.02] active:scale-[0.98]'
                      : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  }`}
                >
                  Надіслати відгук
                </button>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="absolute inset-0 z-50 flex items-center justify-center p-6">
          <div className="bg-white rounded-3xl shadow-2xl max-w-sm w-full">
            <div className="px-6 py-10 text-center">
              <div className="w-16 h-16 bg-green-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Check className="w-8 h-8 text-green-600" strokeWidth={2.5} />
              </div>

              <h2 className="text-2xl font-bold text-gray-900 mb-3">
                Дякуємо за вашу думку!
              </h2>

              <p className="text-gray-600 text-sm mb-8 leading-relaxed">
                Команда Diї дуже вдячна за допомогу. Саме ви будуєте цифрову державу.
              </p>

              <button
                onClick={handleThankYouClose}
                className="w-full bg-white border-2 border-gray-900 text-gray-900 py-4 rounded-2xl font-semibold text-base hover:bg-gray-50 active:bg-gray-100 transition-colors"
              >
                Дякую
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

