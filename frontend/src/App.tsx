import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PhoneMockup } from '@/components/PhoneMockup';
import { HomePage } from '@/pages/HomePage';
import { ClassifierPage } from '@/pages/ClassifierPage';
import { MapPage } from '@/pages/MapPage';
import { ProblemFormPage } from '@/pages/ProblemFormPage';
import { ResultPage } from '@/pages/ResultPage';

// Створюємо React Query клієнт
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1, // Повторити 1 раз при помилці
      refetchOnWindowFocus: false, // Не оновлювати при фокусі вікна
    },
  },
});

function App() {
  const [currentPage, setCurrentPage] = useState<'home' | 'classifier' | 'map' | 'form' | 'result'>('home');
  const [selectedLocation, setSelectedLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [problemText, setProblemText] = useState('');
  const [formContext, setFormContext] = useState<'home' | 'other'>('home');
  const [otherAddressLabel, setOtherAddressLabel] = useState<string | null>(null);

  return (
    <QueryClientProvider client={queryClient}>
      {/* Фон для мокапу - градієнт як у Diia */}
      <div className="min-h-screen bg-gradient-to-b from-blue-400 via-cyan-300 to-yellow-200 flex items-center justify-center p-4">
        {/* iPhone мокап */}
        <PhoneMockup>
          {/* Навігація між сторінками */}
          {currentPage === 'home' && (
            <HomePage onNavigateToClassifier={() => setCurrentPage('classifier')} />
          )}
          
          {currentPage === 'classifier' && (
            <ClassifierPage 
              onBack={() => setCurrentPage('home')}
              onSelectLocation={(type) => {
                if (type === 'other') {
                  setCurrentPage('map');
                } else {
                  // "За місцем проживання" - одразу на форму з хардкодженою адресою
                  setFormContext('home');
                  setOtherAddressLabel(null);
                  setCurrentPage('form');
                }
              }}
            />
          )}
          
          {currentPage === 'map' && (
            <MapPage
              onBack={() => setCurrentPage('classifier')}
              onSelectLocation={({ lat, lng, addressLabel }) => {
                setSelectedLocation({ lat, lng });
                setOtherAddressLabel(addressLabel);
                setFormContext('other');
                setCurrentPage('form');
              }}
            />
          )}
          
          {currentPage === 'form' && (
            <ProblemFormPage
              mode={formContext}
              presetAddress={formContext === 'other' ? otherAddressLabel ?? undefined : undefined}
              onBack={() => setCurrentPage(formContext === 'other' ? 'map' : 'classifier')}
              onSubmit={(text) => {
                setProblemText(text);
                console.log('Опис проблеми:', text);
                setCurrentPage('result');
              }}
            />
          )}
          
          {currentPage === 'result' && (
            <ResultPage
              mode={formContext}
              onBack={() => setCurrentPage('form')}
              onFinish={() => setCurrentPage('home')}
              problemText={problemText}
            />
          )}
        </PhoneMockup>
      </div>
    </QueryClientProvider>
  );
}

export default App;
