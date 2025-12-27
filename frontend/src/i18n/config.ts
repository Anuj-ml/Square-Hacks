import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import { translations } from './translations';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: translations.en },
      hi: { translation: translations.hi },
      mr: { translation: translations.mr }
    },
    lng: localStorage.getItem('language') || 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
