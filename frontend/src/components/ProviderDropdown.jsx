import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';

export default function ProviderDropdown({ provider, setProvider }) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const options = [
    { value: 'ollama', label: 'Local' },
    { value: 'anthropic', label: 'Claude' },
    { value: 'openai', label: 'GPT-4o' }
  ];

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1 bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-zinc-300 text-xs rounded-md px-3 py-1.5 transition-colors shadow-sm"
      >
        {options.find(o => o.value === provider)?.label}
        <ChevronDown className="w-3 h-3 text-zinc-500" />
      </button>

      {isOpen && (
        <div className="absolute bottom-full mb-1 left-1/2 -translate-x-1/2 min-w-[160px] bg-white rounded-md shadow-lg overflow-hidden z-50 border border-zinc-200">
          {options.map((opt) => (
            <div
              key={opt.value}
              onClick={() => {
                setProvider(opt.value);
                setIsOpen(false);
              }}
              className={`px-4 py-2 text-sm cursor-pointer transition-colors text-center font-medium ${
                provider === opt.value
                  ? 'bg-zinc-500 text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-yellow-500 shadow-inner'
                  : 'text-zinc-500 hover:bg-zinc-100'
              }`}
            >
              {opt.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
