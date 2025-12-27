# 🎤 Voice Features Implementation - Web Speech API

## Overview

Implemented comprehensive multilingual voice features using the **Web Speech API** including:

- **Speech Recognition** (Voice Input) - Convert speech to text
- **Speech Synthesis** (Text-to-Speech) - Convert text to speech
- **Multilingual Support** - Works with English, Hindi, Marathi, and more
- **Voice Commands** - Navigate and control the dashboard using voice

## Browser Support

### Speech Recognition
- ✅ Chrome/Edge (Chromium-based)
- ✅ Safari (iOS 14.5+)
- ❌ Firefox (not supported yet)

### Speech Synthesis
- ✅ Chrome/Edge
- ✅ Firefox
- ✅ Safari

## Files Created

### 1. `useSpeechRecognition.ts` Hook
**Location:** `frontend/src/hooks/useSpeechRecognition.ts`

**Features:**
- Start/stop speech recognition
- Multilingual support (maps language codes to Web Speech API locales)
- Real-time transcript and interim results
- Comprehensive error handling
- Continuous and single-shot modes

**API:**
```typescript
const {
  transcript,           // Final recognized text
  interimTranscript,   // Interim results (what's being said)
  isListening,         // Is currently listening
  isSupported,         // Is speech recognition supported
  startListening,      // Start recognition (language, continuous)
  stopListening,       // Stop recognition
  resetTranscript,     // Clear transcript
  error                // Error message if any
} = useSpeechRecognition();
```

**Example:**
```typescript
// Start listening in Hindi
startListening('hi', false); // Single command mode

// Start continuous listening in English
startListening('en', true);  // Continuous mode
```

### 2. `VoiceControl.tsx` Component
**Location:** `frontend/src/components/VoiceControl.tsx`

**Features:**
- Combined UI for speech recognition and text-to-speech
- Real-time visual feedback (listening indicator, transcript display)
- Error messages with helpful hints
- Language-aware (uses current i18n language)
- Command callback for integration

**Props:**
```typescript
interface VoiceControlProps {
  onCommand?: (command: string) => void;  // Callback when command received
  continuous?: boolean;                    // Continuous listening mode
  autoSpeak?: boolean;                     // Auto-speak confirmations
  className?: string;                      // Additional CSS classes
}
```

**Usage:**
```tsx
<VoiceControl 
  continuous={false}
  autoSpeak={false}
  onCommand={(command) => {
    console.log('Received command:', command);
    // Handle navigation, actions, etc.
  }}
/>
```

### 3. Enhanced `useTextToSpeech.ts` Hook
**Location:** `frontend/src/hooks/useTextToSpeech.ts`

**Already existed, now integrated with VoiceControl**

**Features:**
- Speak text in multiple languages
- Voice selection based on language
- Pause/resume/stop controls
- Rate, pitch, and volume control

## Dashboard Integration

### Settings Tab - Voice Module

The Voice Module is integrated into the Settings tab of the Dashboard:

**Location:** Dashboard → Settings → Voice Module

**Features:**
- Toggle switch to enable/disable voice control
- When enabled, shows full VoiceControl component
- Supports voice navigation commands
- Automatically detects language from i18n

**Voice Commands Supported:**

| Command (English) | Command (Hindi) | Command (Marathi) | Action |
|-------------------|-----------------|-------------------|--------|
| "overview" | "अवलोकन" | "आढावा" | Navigate to Overview tab |
| "resources" | "संसाधन" | "संसाधने" | Navigate to Resources tab |
| "decisions" | "निर्णय" | "निर्णय" | Navigate to Decisions tab |
| "advisory" | "सलाह" | "सल्ला" | Navigate to Advisory tab |
| "settings" | "सेटिंग" | "सेटिंग" | Navigate to Settings tab |

## Language Support

### Supported Languages

| Language | Code | Speech Recognition | Text-to-Speech |
|----------|------|-------------------|----------------|
| English | en | en-US | ✅ |
| Hindi | hi | hi-IN | ✅ |
| Marathi | mr | mr-IN | ✅ |
| Tamil | ta | ta-IN | ✅ |
| Telugu | te | te-IN | ✅ |
| Bengali | bn | bn-IN | ✅ |

### Adding New Languages

To add a new language:

1. **Update `useSpeechRecognition.ts`:**
```typescript
const languageMap: Record<string, string> = {
  'en': 'en-US',
  'hi': 'hi-IN',
  'mr': 'mr-IN',
  'your-lang': 'your-lang-locale', // Add here
};
```

2. **Update `useTextToSpeech.ts`:**
```typescript
const languageMap: Record<string, string> = {
  'en': 'en-US',
  'hi': 'hi-IN',
  'mr': 'mr-IN',
  'your-lang': 'your-lang-locale', // Add here
};
```

3. **Add translations** in `translations.ts`

## Translation Keys Added

### English
```typescript
voiceNotSupported: "Voice features not supported in this browser"
startListening: "Start Listening"
stopListening: "Stop Listening"
stopSpeaking: "Stop Speaking"
textToSpeech: "Text to Speech"
listening: "Listening"
speaking: "Speaking"
transcript: "Transcript"
clear: "Clear"
received: "Received"
voiceControlHint: "Click 'Start Listening' to use voice commands..."
voiceModule: "Voice Module"
alwaysOnAssistant: "Always-on Assistant"
voiceModuleDesc: "Multilingual voice commands and text-to-speech."
enable: "Enable"
disable: "Disable"
```

### Hindi (हिंदी)
```typescript
voiceNotSupported: "इस ब्राउज़र में वॉइस सुविधाएं समर्थित नहीं हैं"
startListening: "सुनना शुरू करें"
stopListening: "सुनना बंद करें"
// ... and more
```

### Marathi (मराठी)
```typescript
voiceNotSupported: "या ब्राउझरमध्ये व्हॉइस वैशिष्ट्ये समर्थित नाहीत"
startListening: "ऐकणे सुरू करा"
stopListening: "ऐकणे थांबवा"
// ... and more
```

## Usage Examples

### Example 1: Basic Voice Recognition
```tsx
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';

function MyComponent() {
  const { transcript, isListening, startListening, stopListening } = useSpeechRecognition();

  return (
    <div>
      <button onClick={() => startListening('en', false)}>
        {isListening ? 'Stop' : 'Start'} Listening
      </button>
      <p>You said: {transcript}</p>
    </div>
  );
}
```

### Example 2: Voice Navigation
```tsx
<VoiceControl 
  onCommand={(command) => {
    const lower = command.toLowerCase();
    if (lower.includes('home')) navigate('/');
    if (lower.includes('dashboard')) navigate('/dashboard');
  }}
/>
```

### Example 3: Multilingual TTS
```tsx
import { useTextToSpeech } from '../hooks/useTextToSpeech';
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { speak } = useTextToSpeech();
  const { i18n } = useTranslation();

  const speakMessage = () => {
    speak('Hello, welcome to the dashboard', i18n.language);
  };

  return <button onClick={speakMessage}>Speak</button>;
}
```

## Error Handling

The implementation handles all common errors:

| Error | Message | Solution |
|-------|---------|----------|
| `no-speech` | No speech detected | Speak closer to microphone |
| `audio-capture` | No microphone found | Connect a microphone |
| `not-allowed` | Permission denied | Enable microphone access in browser |
| `network` | Network error | Check internet connection |
| `language-not-supported` | Language not supported | Switch to supported language |

## Testing

### Test Speech Recognition
1. Go to Dashboard → Settings → Voice Module
2. Toggle "Enable"
3. Click "Start Listening"
4. Say a command: "overview", "resources", etc.
5. Watch the transcript appear in real-time
6. Verify navigation happens

### Test Text-to-Speech
1. Use the existing AudioInstructions component
2. Click "Play Instructions"
3. Verify speech in selected language
4. Test pause/resume/stop controls

### Test Multiple Languages
1. Switch language using LanguageSelector (top right)
2. Enable Voice Module
3. Speak in the selected language
4. Verify recognition works
5. Test TTS speaks in correct language

## Browser Console Commands

For debugging, you can test directly in console:

```javascript
// Check if supported
console.log('Recognition:', 'SpeechRecognition' in window);
console.log('Synthesis:', 'speechSynthesis' in window);

// List available voices
window.speechSynthesis.getVoices().forEach(voice => {
  console.log(voice.name, voice.lang);
});
```

## Privacy & Security

### Microphone Permission
- Browser will request microphone permission on first use
- Permission persists for the domain
- Users can revoke in browser settings

### Data Privacy
- All processing happens in the browser (on-device)
- For Chrome: May use Google's speech recognition servers
- No data is stored by the application
- Transcript is kept in component state only

### Best Practices
- Always show visual indicator when listening
- Provide clear error messages
- Allow users to disable voice features
- Don't auto-start listening without user action

## Performance

### Optimization
- Recognition stops automatically when not in continuous mode
- Speech synthesis cancels previous utterances
- No background processing when disabled
- Minimal memory footprint

### Recommendations
- Use single-shot mode for commands (more battery efficient)
- Use continuous mode only when needed
- Stop listening when component unmounts
- Clear transcripts regularly

## Troubleshooting

### Issue: "Voice features not supported"
**Solution:** Use Chrome, Edge, or Safari. Firefox doesn't support Speech Recognition yet.

### Issue: "Microphone permission denied"
**Solution:** 
1. Click the lock icon in browser address bar
2. Allow microphone access
3. Refresh the page

### Issue: Recognition not working in Hindi/Marathi
**Solution:**
1. Ensure you're using Chrome/Edge (best support)
2. Check language selector is set correctly
3. Speak clearly and at normal pace
4. Try switching to English to test if it's a language issue

### Issue: No voices available for TTS
**Solution:**
1. Wait a few seconds after page load (voices load async)
2. Check browser settings → Languages
3. On mobile, ensure language packs are downloaded

## Future Enhancements

Possible additions:
- [ ] Voice authentication
- [ ] Custom wake word ("Hey Dashboard")
- [ ] Voice search in medical documents
- [ ] Voice-controlled data entry
- [ ] Speech-to-text for doctor notes
- [ ] Real-time translation
- [ ] Voice biometrics for patient identification

## Resources

- [Web Speech API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [SpeechRecognition API](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition)
- [SpeechSynthesis API](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis)
- [Browser Support - Can I Use](https://caniuse.com/speech-recognition)

---

## Summary

✅ **Speech Recognition** - Fully implemented with multilingual support  
✅ **Text-to-Speech** - Enhanced with language-aware voices  
✅ **Voice Commands** - Integrated with Dashboard navigation  
✅ **UI Components** - Complete VoiceControl component  
✅ **Translations** - All keys added in English, Hindi, Marathi  
✅ **Error Handling** - Comprehensive error messages  
✅ **Documentation** - Complete usage guide  

**Ready to use!** Enable Voice Module in Settings tab.
