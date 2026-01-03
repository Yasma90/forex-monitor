'use client';

import { useState, useRef, useEffect } from 'react';
import { ChevronDown, ArrowLeftRight } from 'lucide-react';

export interface Currency {
  code: string;
  name: string;
  symbol: string;
  flag: string;
}

export const CURRENCIES: Currency[] = [
  { code: 'USD', name: 'Dólar estadounidense', symbol: '$', flag: '🇺🇸' },
  { code: 'EUR', name: 'Euro', symbol: '€', flag: '🇪🇺' },
  { code: 'GBP', name: 'Libra esterlina', symbol: '£', flag: '🇬🇧' },
  { code: 'JPY', name: 'Yen japonés', symbol: '¥', flag: '🇯🇵' },
  { code: 'CHF', name: 'Franco suizo', symbol: 'Fr', flag: '🇨🇭' },
  { code: 'CAD', name: 'Dólar canadiense', symbol: 'C$', flag: '🇨🇦' },
  { code: 'AUD', name: 'Dólar australiano', symbol: 'A$', flag: '🇦🇺' },
  { code: 'CNY', name: 'Yuan chino', symbol: '¥', flag: '🇨🇳' },
  { code: 'MXN', name: 'Peso mexicano', symbol: '$', flag: '🇲🇽' },
  { code: 'BRL', name: 'Real brasileño', symbol: 'R$', flag: '🇧🇷' },
  { code: 'ARS', name: 'Peso argentino', symbol: '$', flag: '🇦🇷' },
  { code: 'CLP', name: 'Peso chileno', symbol: '$', flag: '🇨🇱' },
  { code: 'COP', name: 'Peso colombiano', symbol: '$', flag: '🇨🇴' },
  { code: 'PEN', name: 'Sol peruano', symbol: 'S/', flag: '🇵🇪' },
];

interface CurrencySelectorProps {
  baseCurrency: string;
  targetCurrency: string;
  onBaseChange: (code: string) => void;
  onTargetChange: (code: string) => void;
  onSwap: () => void;
}

function CurrencyDropdown({
  value,
  onChange,
  exclude,
  label
}: {
  value: string;
  onChange: (code: string) => void;
  exclude: string;
  label: string;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const selected = CURRENCIES.find(c => c.code === value);
  const options = CURRENCIES.filter(c => c.code !== exclude);

  return (
    <div className="relative" ref={ref}>
      <label className="text-xs text-gray-500 dark:text-gray-400 mb-1 block">{label}</label>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-gray-300 dark:hover:border-gray-600 transition-colors min-w-[140px]"
      >
        <span className="text-lg">{selected?.flag}</span>
        <span className="font-medium text-gray-900 dark:text-white">{value}</span>
        <ChevronDown className={`w-4 h-4 ml-auto text-gray-500 dark:text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-56 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-50 max-h-64 overflow-y-auto">
          {options.map((currency) => (
            <button
              key={currency.code}
              onClick={() => {
                onChange(currency.code);
                setIsOpen(false);
              }}
              className={`w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
                currency.code === value ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400' : 'text-gray-700 dark:text-gray-300'
              }`}
            >
              <span className="text-lg">{currency.flag}</span>
              <span className="font-medium">{currency.code}</span>
              <span className="text-gray-500 dark:text-gray-400 text-xs truncate">{currency.name}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function CurrencySelector({
  baseCurrency,
  targetCurrency,
  onBaseChange,
  onTargetChange,
  onSwap
}: CurrencySelectorProps) {
  return (
    <div className="flex items-end gap-2">
      <CurrencyDropdown
        value={baseCurrency}
        onChange={onBaseChange}
        exclude={targetCurrency}
        label="Base"
      />

      <button
        onClick={onSwap}
        className="p-2 mb-0.5 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
        title="Intercambiar divisas"
      >
        <ArrowLeftRight className="w-4 h-4 text-gray-600 dark:text-gray-400" />
      </button>

      <CurrencyDropdown
        value={targetCurrency}
        onChange={onTargetChange}
        exclude={baseCurrency}
        label="Destino"
      />
    </div>
  );
}
