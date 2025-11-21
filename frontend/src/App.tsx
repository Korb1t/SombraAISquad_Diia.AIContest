import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PhoneMockup } from '@/components/PhoneMockup';
import { HomePage } from '@/pages/HomePage';
import { ClassifierPage } from '@/pages/ClassifierPage';
import { MapPage } from '@/pages/MapPage';
import { ProblemFormPage } from '@/pages/ProblemFormPage';
import { ResultPage } from '@/pages/ResultPage';
import type { SolveProblemResponse } from '@/types/api';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  const [currentPage, setCurrentPage] = useState<'home' | 'classifier' | 'map' | 'form' | 'result'>('home');
  const [selectedLocation, setSelectedLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [problemText, setProblemText] = useState('');
  const [formContext, setFormContext] = useState<'home' | 'other'>('home');
  const [otherAddressLabel, setOtherAddressLabel] = useState<string | null>(null);
  const [apiResponse, setApiResponse] = useState<SolveProblemResponse | null>(null);

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gradient-to-b from-blue-400 via-cyan-300 to-yellow-200 flex items-center justify-center p-4">
        <PhoneMockup>
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
              onSubmit={(text, response) => {
                setProblemText(text);
                setApiResponse(response);
                console.log('Опис проблеми:', text);
                console.log('API відповідь:', response);
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
              apiResponse={apiResponse}
            />
          )}
        </PhoneMockup>
      </div>
    </QueryClientProvider>
  );
}

export default App;
