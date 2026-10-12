import React, { useState } from 'react';
import { X, Mail, Lock } from 'lucide-react';

export default function LoginModal({ isOpen, onClose, onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (email && password) {
      onLogin({ email });
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-surface border border-border w-full max-w-md rounded-xl shadow-2xl p-6 relative">
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 text-zinc-400 hover:text-zinc-200 p-1"
        >
          <X className="w-5 h-5" />
        </button>
        
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-zinc-100 mb-2">Welcome Back</h2>
          <p className="text-zinc-400 text-sm">Sign in to sync your chats and preferences.</p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input 
                type="email" 
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-zinc-900 border border-zinc-700 text-zinc-200 rounded-md py-2 pl-9 pr-3 text-sm focus:outline-none focus:border-indigo-500"
                placeholder="you@example.com"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input 
                type="password" 
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-zinc-900 border border-zinc-700 text-zinc-200 rounded-md py-2 pl-9 pr-3 text-sm focus:outline-none focus:border-indigo-500"
                placeholder="••••••••"
              />
            </div>
          </div>
          
          <button 
            type="submit"
            className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2 rounded-md transition-colors text-sm mt-4"
          >
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
}
