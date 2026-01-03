'use client';

import { useState, useRef, useEffect } from 'react';
import { FileDown, FileSpreadsheet, FileJson, FileText, ChevronDown } from 'lucide-react';
import { exportData, ExportFormat } from '@/lib/api';

interface ExportMenuProps {
  baseCurrency: string;
  targetCurrency: string;
  days?: number;
  disabled?: boolean;
}

const exportOptions: { format: ExportFormat; label: string; icon: React.ReactNode }[] = [
  { format: 'csv', label: 'CSV', icon: <FileText className="w-4 h-4" /> },
  { format: 'excel', label: 'Excel', icon: <FileSpreadsheet className="w-4 h-4" /> },
  { format: 'json', label: 'JSON', icon: <FileJson className="w-4 h-4" /> },
];

export default function ExportMenu({ baseCurrency, targetCurrency, days = 30, disabled }: ExportMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleExport = async (format: ExportFormat) => {
    setLoading(true);
    setIsOpen(false);
    try {
      await exportData(format, baseCurrency, targetCurrency, days);
    } catch (err) {
      console.error(`Error exporting ${format}:`, err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={disabled || loading}
        className="flex items-center gap-1.5 px-3 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors disabled:opacity-50"
        title="Exportar datos"
      >
        <FileDown className={`w-4 h-4 ${loading ? 'animate-pulse' : ''}`} />
        <span className="hidden sm:inline text-sm">Exportar</span>
        <ChevronDown className={`w-3 h-3 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-1 w-36 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
          {exportOptions.map((option) => (
            <button
              key={option.format}
              onClick={() => handleExport(option.format)}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
            >
              {option.icon}
              <span>{option.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
