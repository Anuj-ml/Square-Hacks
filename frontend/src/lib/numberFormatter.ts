// Number formatter utility for localizing numbers based on selected language

const localeMap: Record<string, string> = {
  en: 'en-US',
  hi: 'hi-IN',
  mr: 'mr-IN',
  ta: 'ta-IN',
  te: 'te-IN',
  bn: 'bn-IN'
};

// Numbering system for each language
const numberingSystemMap: Record<string, string> = {
  en: 'latn',  // Western Arabic numerals (0-9)
  hi: 'deva',  // Devanagari numerals (०-९)
  mr: 'deva',  // Devanagari numerals (०-९)
  ta: 'tamldec', // Tamil numerals
  te: 'telu',  // Telugu numerals
  bn: 'beng'   // Bengali numerals
};

export const formatNumber = (num: number, language: string = 'en'): string => {
  const locale = localeMap[language] || 'en-US';
  const numberingSystem = numberingSystemMap[language] || 'latn';
  
  return new Intl.NumberFormat(locale, {
    numberingSystem: numberingSystem
  }).format(num);
};

export const formatPercent = (num: number, language: string = 'en'): string => {
  const locale = localeMap[language] || 'en-US';
  const numberingSystem = numberingSystemMap[language] || 'latn';
  
  return new Intl.NumberFormat(locale, { 
    style: 'percent',
    minimumFractionDigits: 0,
    maximumFractionDigits: 1,
    numberingSystem: numberingSystem
  }).format(num / 100);
};

export const formatDecimal = (num: number, language: string = 'en', decimals: number = 1): string => {
  const locale = localeMap[language] || 'en-US';
  const numberingSystem = numberingSystemMap[language] || 'latn';
  
  return new Intl.NumberFormat(locale, { 
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
    numberingSystem: numberingSystem
  }).format(num);
};

export const formatCurrency = (num: number, language: string = 'en'): string => {
  const locale = localeMap[language] || 'en-US';
  const numberingSystem = numberingSystemMap[language] || 'latn';
  
  return new Intl.NumberFormat(locale, { 
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
    numberingSystem: numberingSystem
  }).format(num);
};
