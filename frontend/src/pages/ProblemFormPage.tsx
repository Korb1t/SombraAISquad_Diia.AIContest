import { useState, useEffect, useRef } from 'react';
import { ArrowLeft, Edit2, Square, Mic } from 'lucide-react';
import { Loader } from '@/components/Loader';
import { ErrorModal } from '@/components/ErrorModal';
import { useSolveProblem } from '@/api/hooks';
import type { SolveProblemResponse } from '@/types/api';

interface ProblemFormPageProps {
  onBack: () => void;
  mode?: 'home' | 'other';
  presetAddress?: string;
  onSubmit: (problemText: string, apiResponse: SolveProblemResponse) => void;
}

export function ProblemFormPage({
  onBack,
  onSubmit,
  mode = 'home',
  presetAddress,
}: ProblemFormPageProps) {
  const [problemText, setProblemText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [showAddressModal, setShowAddressModal] = useState(false);
  const [showErrorModal, setShowErrorModal] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [editedAddress, setEditedAddress] = useState('');
  const recognitionRef = useRef<any>(null);
  const finalTranscriptRef = useRef('');
  
  const { mutate: solveProblem, isPending } = useSolveProblem();
  
  const defaultAddress =
    'Аральська, 8';
  const [currentAddress, setCurrentAddress] = useState(defaultAddress);
  const isHomeMode = mode === 'home';
  const headerTitle = isHomeMode ? 'За місцем проживання' : 'Інша Адреса';
  const displayAddress = isHomeMode
    ? currentAddress
    : presetAddress || 'Обрана адреса';
  
  const parseAddress = (fullAddress: string) => {
    const parts = fullAddress.split(',').map(p => p.trim());
    
    const isCity = (p: string) => p.toLowerCase().startsWith('місто') || p.toLowerCase().startsWith('м.');
    const isRegion = (p: string) => p.toLowerCase().includes('область');
    const isCountry = (p: string) => p.toLowerCase() === 'україна';
    const isApartment = (p: string) => /^(кв\.?|квартира)\s*\d+/i.test(p);
    const isStreetExplicit = (p: string) => p.toLowerCase().includes('вулиця') || p.toLowerCase().includes('вул.');

    const cityPart = parts.find(isCity);
    const city = cityPart?.replace(/місто |м\./gi, '').trim() || 'Львів';
    
    // Find street part - either explicit or by elimination
    let streetIndex = parts.findIndex(isStreetExplicit);
    if (streetIndex === -1) {
      streetIndex = parts.findIndex(p => !isCity(p) && !isRegion(p) && !isCountry(p) && !isApartment(p));
    }

    let streetPart = streetIndex !== -1 ? parts[streetIndex] : undefined;
    
    if (streetPart) {
      // Check if the next part is the street number (e.g. "вулиця Аральська, 8")
      if (streetIndex + 1 < parts.length) {
        const nextPart = parts[streetIndex + 1];
        // If next part starts with a digit and doesn't look like apartment info
        if (/^\d/.test(nextPart) && !isApartment(nextPart)) {
          streetPart = `${streetPart}, ${nextPart}`;
        }
      }

      // Ensure format <street_name>, <street_number> if number is in the same string
      // e.g. "вулиця Аральська 8" -> "вулиця Аральська, 8"
      const match = streetPart.match(/^(.*?)(\s+\d+\S*)$/);
      if (match) {
        const prefix = match[1].trim();
        const number = match[2].trim();
        if (!prefix.endsWith(',')) {
          streetPart = `${prefix}, ${number}`;
        }
      }

      // Remove "вулиця" prefix to return only "Street, Number"
      streetPart = streetPart.replace(/^(вулиця|вул\.)\s*/i, '');
    }

    const address = streetPart || fullAddress;
    
    // Extract apartment number from address (look for "кв XX" or "квартира XX")
    const apartmentMatch = fullAddress.match(/(?:кв\.?|квартира)\s*(\d+)/i);
    const apartment = apartmentMatch ? apartmentMatch[1] : '';
    
    return { city, address, apartment };
  };
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'uk-UA';

      recognitionRef.current.onresult = (event: any) => {
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscriptRef.current += transcript + ' ';
          } else {
            interimTranscript = transcript;
          }
        }

        const fullText = finalTranscriptRef.current + interimTranscript;
        setProblemText(fullText);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
      };

      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      finalTranscriptRef.current = '';
    };
  }, []);

  const toggleRecording = () => {
    if (!recognitionRef.current) {
      alert('Голосове введення не підтримується вашим браузером. Спробуйте Chrome або Edge.');
      return;
    }

    if (isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    } else {
      finalTranscriptRef.current = problemText;
      recognitionRef.current.start();
      setIsRecording(true);
    }
  };

  const handleSubmit = () => {
    if (problemText.trim()) {
      const { city, address, apartment } = parseAddress(displayAddress);
      
      solveProblem({
        user_info: {
          name: 'Василь Васильович Байдак',
          address: address,
          city: city,
          phone: '+380123456789',
          apartment: apartment,
        },
        problem_text: problemText.trim(),
      }, {
        onSuccess: (data) => {
          console.log('API відповідь:', data);
          onSubmit(problemText.trim(), data);
        },
        onError: (error: any) => {
          console.error('Помилка API:', error);
          let errorMsg = 'Зачекайте та спробуйте ще раз.';
          
          if (error?.response?.data?.detail) {
            const detail = error.response.data.detail;
            if (typeof detail === 'string') {
              errorMsg = detail;
            } else if (Array.isArray(detail)) {
              errorMsg = detail.map((d: any) => d.msg || JSON.stringify(d)).join(', ');
            } else {
              errorMsg = JSON.stringify(detail);
            }
          }
          
          setErrorMessage(errorMsg);
          setShowErrorModal(true);
        },
      });
    }
  };

  const isFormValid = problemText.trim().length > 0;

  if (isPending) {
    return <Loader />;
  }

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
            {headerTitle}
          </h1>
        </div>
      </div>

      <div className="flex-1 px-6 py-6 overflow-y-auto pb-28">
        <div className="bg-white rounded-2xl p-5 mb-4 shadow-sm">
          <p className="text-gray-700 text-sm leading-relaxed whitespace-pre-line">
            {isHomeMode ? 'Місце проживання зазначено в банку:\n' : ''}
            {displayAddress}
          </p>
        </div>

        {isHomeMode && (
          <button 
            onClick={() => {
              setEditedAddress(currentAddress);
              setShowAddressModal(true);
            }}
            className="w-full bg-gray-100 border-2 border-gray-300 rounded-2xl px-5 py-4 mb-8 flex items-center justify-center gap-2 hover:bg-gray-200 hover:border-gray-400 transition-colors"
          >
            <Edit2 className="w-5 h-5 text-gray-700" strokeWidth={2} />
            <span className="text-gray-900 font-medium text-[15px]">
              Змінити
            </span>
          </button>
        )}

        <h2 className="text-gray-900 font-semibold text-base mb-3">
          Сформувати запит про проблему
        </h2>

        <div className="bg-white rounded-2xl shadow-sm relative">
          <textarea
            value={problemText}
            onChange={(e) => setProblemText(e.target.value)}
            placeholder="Опиши або надиктуй проблему"
            disabled={isRecording}
            className="w-full h-48 px-5 py-4 pr-16 text-gray-900 text-[15px] leading-relaxed rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-400/80 focus:ring-offset-0 placeholder:text-gray-400 disabled:bg-white"
            style={{ outline: 'none' }}
          />
          
          {isRecording && (
            <div className="absolute bottom-5 left-5 right-20 flex items-end gap-0.5 h-5">
              {Array.from({ length: 30 }).map((_, i) => (
                <div
                  key={i}
                  className="flex-1 bg-gray-300 rounded-full animate-pulse"
                  style={{
                    height: `${30 + Math.random() * 70}%`,
                    animationDelay: `${i * 0.05}s`,
                    animationDuration: `${0.5 + Math.random() * 0.5}s`,
                  }}
                />
              ))}
            </div>
          )}
          
          <button 
            className={`absolute bottom-4 right-4 w-10 h-10 rounded-full flex items-center justify-center hover:scale-105 active:scale-95 transition-all ${
              isRecording ? 'bg-black animate-pulse' : 'bg-black'
            }`}
            onClick={toggleRecording}
          >
            {isRecording ? (
              <Square className="w-4 h-4 text-white fill-white" strokeWidth={0} />
            ) : (
              <Mic className="w-5 h-5 text-white" strokeWidth={2.5} />
            )}
          </button>
        </div>
      </div>

      <div className="absolute bottom-5 left-0 right-0 px-6 py-4 bg-gray-100">
        <button
          onClick={handleSubmit}
          disabled={!isFormValid}
          className={`
            w-full py-4 rounded-2xl font-semibold text-base transition-all
            ${isFormValid 
              ? 'bg-black text-white hover:scale-[1.02] active:scale-[0.98]' 
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }
          `}
        >
          Сформувати Запит
        </button>
      </div>

      {showAddressModal && isHomeMode && (
        <div className="absolute inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 px-6">
          <div className="bg-white rounded-3xl p-6 w-full max-w-sm shadow-2xl">
            <h2 className="text-xl font-bold text-gray-900 text-center mb-6">
              Нова Адреса
            </h2>

            <textarea
              value={editedAddress}
              onChange={(e) => setEditedAddress(e.target.value)}
              placeholder="Введіть адресу"
              className="w-full bg-gray-50 rounded-2xl px-5 py-4 mb-6 text-gray-700 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-400 focus:bg-white transition-colors"
              rows={4}
              style={{ outline: 'none' }}
            />

            <button
              className="w-full bg-black text-white py-4 rounded-2xl font-semibold text-base mb-3 hover:scale-[1.02] active:scale-[0.98] transition-transform disabled:bg-gray-300 disabled:cursor-not-allowed"
              disabled={!editedAddress.trim()}
              onClick={() => {
                if (editedAddress.trim()) {
                  setCurrentAddress(editedAddress.trim());
                  setShowAddressModal(false);
                }
              }}
            >
              Зберегти
            </button>

            <button
              className="w-full bg-white border-2 border-gray-900 text-gray-900 py-4 rounded-2xl font-semibold text-base hover:bg-gray-200 active:bg-gray-300 transition-colors"
              onClick={() => {
                setEditedAddress(currentAddress);
                setShowAddressModal(false);
              }}
            >
              Скасувати
            </button>
          </div>
        </div>
      )}

      <ErrorModal
        isOpen={showErrorModal}
        onClose={() => setShowErrorModal(false)}
        message={errorMessage}
      />
    </div>
  );
}

