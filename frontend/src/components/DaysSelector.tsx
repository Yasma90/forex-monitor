'use client';

import { Calendar } from 'lucide-react';

interface DaysSelectorProps {
  value: number;
  onChange: (days: number) => void;
}

const OPTIONS = [
  { value: 7, label: '7d' },
  { value: 30, label: '30d' },
  { value: 90, label: '90d' },
  { value: 180, label: '6m' },
  { value: 365, label: '1a' },
];

export default function DaysSelector({ value, onChange }: DaysSelectorProps) {
  return (
    <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
      <Calendar className="w-4 h-4 text-gray-500 ml-2" />
      {OPTIONS.map((opt) => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
            value === opt.value
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
