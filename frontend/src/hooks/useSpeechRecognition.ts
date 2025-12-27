import { useState, useEffect, useCallback, useRef } from 'react';

interface UseSpeechRecognitionReturn {
  transcript: string;
  interimTranscript: string;
  isListening: boolean;
  isSupported: boolean;
  startListening: (language?: string, continuous?: boolean) => void;
  stopListening: () => void;
  resetTranscript: () => void;
  error: string | null;
}

// Extend Window interface for Web Speech API
declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition;
    webkitSpeechRecognition: typeof SpeechRecognition;
  }
}

export function useSpeechRecognition(): UseSpeechRecognitionReturn {
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  useEffect(() => {
    // Check for Speech Recognition API support
    const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognitionAPI) {
      setIsSupported(true);
      recognitionRef.current = new SpeechRecognitionAPI();
      
      const recognition = recognitionRef.current;
      
      // Configure recognition
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;
      
      // Event handlers
      recognition.onstart = () => {
        setIsListening(true);
        setError(null);
        console.log('🎤 Speech recognition started');
      };

      recognition.onend = () => {
        setIsListening(false);
        console.log('🎤 Speech recognition ended');
      };

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        let interimText = '';
        let finalText = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          const transcriptText = result[0].transcript;

          if (result.isFinal) {
            finalText += transcriptText + ' ';
          } else {
            interimText += transcriptText;
          }
        }

        setInterimTranscript(interimText);
        
        if (finalText) {
          setTranscript(prev => prev + finalText);
          setInterimTranscript('');
        }
      };

      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        console.error('🎤 Speech recognition error:', event.error);
        
        const errorMessages: Record<string, string> = {
          'no-speech': 'No speech detected. Please try again.',
          'audio-capture': 'No microphone found. Please connect a microphone.',
          'not-allowed': 'Microphone permission denied. Please enable microphone access.',
          'network': 'Network error. Please check your internet connection.',
          'aborted': 'Speech recognition aborted.',
          'service-not-allowed': 'Speech recognition service not allowed.',
          'bad-grammar': 'Grammar error in speech recognition.',
          'language-not-supported': 'Language not supported.'
        };
        
        setError(errorMessages[event.error] || `Speech recognition error: ${event.error}`);
        setIsListening(false);
      };

      recognition.onnomatch = () => {
        console.warn('🎤 No speech match found');
        setError('No speech match found. Please speak clearly.');
      };

    } else {
      console.warn('Speech Recognition API not supported in this browser');
      setIsSupported(false);
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {
          // Ignore errors on cleanup
        }
      }
    };
  }, []);

  const startListening = useCallback((language: string = 'en', continuous: boolean = false) => {
    if (!isSupported || !recognitionRef.current) {
      setError('Speech recognition not supported');
      return;
    }

    try {
      // Language mapping for Web Speech API
      const languageMap: Record<string, string> = {
        'en': 'en-US',
        'hi': 'hi-IN',
        'mr': 'mr-IN',
        'ta': 'ta-IN',
        'te': 'te-IN',
        'bn': 'bn-IN',
        'es': 'es-ES',
        'fr': 'fr-FR',
        'de': 'de-DE',
        'ja': 'ja-JP',
        'zh': 'zh-CN'
      };

      const recognitionLang = languageMap[language] || 'en-US';
      
      recognitionRef.current.lang = recognitionLang;
      recognitionRef.current.continuous = continuous;
      
      // Reset previous state
      setError(null);
      setInterimTranscript('');
      
      recognitionRef.current.start();
      console.log(`🎤 Starting speech recognition in ${recognitionLang} (continuous: ${continuous})`);
    } catch (err) {
      console.error('Error starting speech recognition:', err);
      setError('Failed to start speech recognition');
    }
  }, [isSupported]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      try {
        recognitionRef.current.stop();
      } catch (err) {
        console.error('Error stopping speech recognition:', err);
      }
    }
  }, [isListening]);

  const resetTranscript = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
    setError(null);
  }, []);

  return {
    transcript,
    interimTranscript,
    isListening,
    isSupported,
    startListening,
    stopListening,
    resetTranscript,
    error
  };
}
