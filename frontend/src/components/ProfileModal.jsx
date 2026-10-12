import React from 'react';
import { X, User, LogOut } from 'lucide-react';

export default function ProfileModal({ isOpen, onClose, user, onLogout }) {
  if (!isOpen || !user) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-surface border border-border w-full max-w-sm rounded-xl shadow-2xl p-6 relative">
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 text-zinc-400 hover:text-zinc-200 p-1"
        >
          <X className="w-5 h-5" />
        </button>
        
        <div className="mb-6 flex flex-col items-center">
          <div className="w-20 h-20 rounded-full bg-indigo-600 flex items-center justify-center text-white text-2xl font-bold mb-4">
            {user.email.charAt(0).toUpperCase()}
          </div>
          <h2 className="text-xl font-bold text-zinc-100">{user.email}</h2>
          <span className="text-xs text-zinc-400 mt-1">Free Tier</span>
        </div>
        
        <div className="space-y-2 border-t border-border pt-4">
          <button className="w-full flex items-center gap-3 px-4 py-2 text-sm text-zinc-300 hover:bg-zinc-800 hover:text-zinc-100 rounded-md transition-colors">
            <User className="w-4 h-4" />
            Account Settings
          </button>
          <button 
            onClick={() => {
              onLogout();
              onClose();
            }}
            className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-400 hover:bg-red-500/10 hover:text-red-300 rounded-md transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}
