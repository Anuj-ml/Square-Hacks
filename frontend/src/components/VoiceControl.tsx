import React, { useEffect, useState } from 'react';
import { Mic, MicOff, Volume2, VolumeX } from 'lucide-react';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';
import { useTextToSpeech } from '../hooks/useTextToSpeech';
import { useTranslation } from 'react-i18next';

interface VoiceControlProps {
  onCommand?: (command: string) => void;
  continuous?: boolean;
  autoSpeak?: boolean;
  className?: string;
}

export const VoiceControl: React.FC<VoiceControlProps> = ({
  onCommand,
  continuous = false,
  autoSpeak = false,
  className = ''
}) => {
  const { t, i18n } = useTranslation();
  const {
    transcript,
    interimTranscript,
    isListening,
    isSupported: recognitionSupported,
    startListening,
    stopListening,
    resetTranscript,
    error: recognitionError
  } = useSpeechRecognition();

  const {
    speak,
    stop: stopSpeaking,
    isSpeaking,
    isSupported: ttsSupported
  } = useTextToSpeech();

  const [lastCommand, setLastCommand] = useState<string>('');

  // Handle voice commands
  useEffect(() => {
    if (transcript && transcript !== lastCommand) {
      setLastCommand(transcript);
      
      if (onCommand) {
        onCommand(transcript);
      }

      // Auto-speak confirmation if enabled
      if (autoSpeak && ttsSupported) {
        const confirmation = `${t('received')}: ${transcript}`;
        speak(confirmation, i18n.language);
      }
    }
  }, [transcript, lastCommand, onCommand, autoSpeak, speak, ttsSupported, i18n.language, t]);

  const handleToggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      resetTranscript();
      startListening(i18n.language, continuous);
    }
  };

  const handleToggleSpeaking = () => {
    if (isSpeaking) {
      stopSpeaking();
    }
  };

  if (!recognitionSupported && !ttsSupported) {
    return (
      <div className={`p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg ${className}`}>
        <p className="text-sm text-yellow-400">
          ⚠️ {t('voiceNotSupported')}
        </p>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Control Buttons */}
      <div className="flex items-center gap-3">
        {/* Speech Recognition Button */}
        {recognitionSupported && (
          <button
            onClick={handleToggleListening}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 ${
              isListening
                ? 'bg-red-600 hover:bg-red-700 animate-pulse'
                : 'bg-blue-500 hover:bg-blue-600'
            } text-white font-medium shadow-lg hover:shadow-xl`}
            title={isListening ? t('stopListening') : t('startListening')}
          >
            {isListening ? (
              <>
                <MicOff className="w-4 h-4" />
                <span className="text-sm">{t('stopListening')}</span>
              </>
            ) : (
              <>
                <Mic className="w-4 h-4" />
                <span className="text-sm">{t('startListening')}</span>
              </>
            )}
          </button>
        )}

        {/* Text-to-Speech Button */}
        {ttsSupported && (
          <button
            onClick={handleToggleSpeaking}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 ${
              isSpeaking
                ? 'bg-purple-600 hover:bg-purple-700'
                : 'bg-gray-500 hover:bg-gray-600'
            } text-white font-medium shadow-lg hover:shadow-xl`}
            title={isSpeaking ? t('stopSpeaking') : t('textToSpeech')}
            disabled={!isSpeaking}
          >
            {isSpeaking ? (
              <>
                <VolumeX className="w-4 h-4" />
                <span className="text-sm">{t('stopSpeaking')}</span>
              </>
            ) : (
              <>
                <Volume2 className="w-4 h-4" />
                <span className="text-sm">{t('textToSpeech')}</span>
              </>
            )}
          </button>
        )}

        {/* Language Indicator */}
        <div className="px-3 py-2 bg-[var(--element-bg)] border border-[var(--border-main)] rounded-lg">
          <span className="text-xs font-mono text-[var(--text-secondary)]">
            {i18n.language.toUpperCase()}
          </span>
        </div>
      </div>

      {/* Status Display */}
      <div className="space-y-2">
        {/* Listening Status */}
        {isListening && (
          <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg animate-fadeIn">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
              <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider">
                {t('listening')}
              </span>
            </div>
            
            {/* Interim Transcript */}
            {interimTranscript && (
              <p className="text-sm text-gray-400 italic">
                {interimTranscript}
              </p>
            )}
          </div>
        )}

        {/* Transcript Display */}
        {transcript && (
          <div className="p-4 bg-[var(--element-bg)] border border-[var(--border-main)] rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider">
                {t('transcript')}
              </span>
              <button
                onClick={resetTranscript}
                className="text-xs text-gray-500 hover:text-[var(--text-primary)] transition-colors"
              >
                {t('clear')}
              </button>
            </div>
            <p className="text-sm text-[var(--text-primary)] leading-relaxed">
              {transcript}
            </p>
          </div>
        )}

        {/* Error Display */}
        {recognitionError && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg animate-fadeIn">
            <p className="text-sm text-red-400">
              ⚠️ {recognitionError}
            </p>
          </div>
        )}

        {/* Speaking Status */}
        {isSpeaking && (
          <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-lg animate-fadeIn">
            <div className="flex items-center gap-2">
              <Volume2 className="w-4 h-4 text-purple-400 animate-pulse" />
              <span className="text-xs font-semibold text-purple-400 uppercase tracking-wider">
                {t('speaking')}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Help Text */}
      {!isListening && !transcript && (
        <div className="p-3 bg-[var(--element-bg)] border border-[var(--border-subtle)] rounded-lg">
          <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
            💡 {t('voiceControlHint')}
          </p>
        </div>
      )}
    </div>
  );
};
