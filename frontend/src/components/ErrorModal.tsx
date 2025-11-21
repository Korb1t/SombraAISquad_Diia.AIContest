import { AlertCircle } from 'lucide-react';

interface ErrorModalProps {
  isOpen: boolean;
  onClose: () => void;
  message?: string;
}

export function ErrorModal({ isOpen, onClose, message }: ErrorModalProps) {
  if (!isOpen) return null;

  return (
    <>
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm z-50" />

      <div className="absolute inset-0 z-50 flex items-center justify-center p-6">
        <div className="bg-white rounded-3xl shadow-2xl max-w-sm w-full">
          <div className="px-6 py-10 text-center">
            <div className="w-16 h-16 bg-red-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <AlertCircle className="w-8 h-8 text-red-600" strokeWidth={2.5} />
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              Ой, виникла помилка!
            </h2>

            <p className="text-gray-600 text-sm mb-8 leading-relaxed">
              {message || 'Зачекайте та спробуйте ще раз.'}
            </p>

            <button
              onClick={onClose}
              className="w-full bg-black text-white py-4 rounded-2xl font-semibold text-base hover:scale-[1.02] active:scale-[0.98] transition-transform"
            >
              Повернутись назад
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

