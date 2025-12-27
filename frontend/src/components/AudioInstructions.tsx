import React, { useEffect } from 'react';
import { Volume2, VolumeX, Pause, Play } from 'lucide-react';
import { useTextToSpeech } from '../hooks/useTextToSpeech';
import { useTranslation } from 'react-i18next';

interface AudioInstructionsProps {
  text: string;
  autoPlay?: boolean;
  showText?: boolean;
  className?: string;
}

export const AudioInstructions: React.FC<AudioInstructionsProps> = ({
  text,
  autoPlay = false,
  showText = true,
  className = ''
}) => {
  const { i18n } = useTranslation();
  const { speak, stop, pause, resume, isSpeaking, isPaused, isSupported } = useTextToSpeech();

  useEffect(() => {
    if (autoPlay && text && isSupported) {
      setTimeout(() => {
        speak(text, i18n.language);
      }, 500);
    }

    return () => {
      stop();
    };
  }, [text, autoPlay]);

  if (!isSupported) {
    return (
      <div className="text-sm text-gray-400">
        ⚠️ Text-to-speech not supported in this browser
      </div>
    );
  }

  const handleClick = () => {
    if (isSpeaking) {
      if (isPaused) {
        resume();
      } else {
        pause();
      }
    } else {
      speak(text, i18n.language);
    }
  };

  const handleStop = (e: React.MouseEvent) => {
    e.stopPropagation();
    stop();
  };

  return (
    <div className={`flex items-start gap-3 ${className}`}>
      <div className="flex items-center gap-2">
        <button
          onClick={handleClick}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 ${
            isSpeaking
              ? 'bg-blue-600 hover:bg-blue-700'
              : 'bg-blue-500 hover:bg-blue-600'
          } text-white font-medium shadow-lg hover:shadow-xl`}
          title={isSpeaking ? (isPaused ? 'Resume' : 'Pause') : 'Play audio'}
        >
          {isSpeaking ? (
            isPaused ? (
              <Play className="w-4 h-4" />
            ) : (
              <Pause className="w-4 h-4" />
            )
          ) : (
            <Volume2 className="w-4 h-4" />
          )}
          <span className="text-sm">
            {isSpeaking ? (isPaused ? 'Resume' : 'Pause') : 'Play Instructions'}
          </span>
        </button>

        {isSpeaking && (
          <button
            onClick={handleStop}
            className="p-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
            title="Stop audio"
          >
            <VolumeX className="w-4 h-4" />
          </button>
        )}
      </div>

      {showText && (
        <div className="flex-1 p-3 bg-surface/50 rounded-lg border border-white/10">
          <p className="text-sm text-gray-300 leading-relaxed">{text}</p>
        </div>
      )}
    </div>
  );
};
