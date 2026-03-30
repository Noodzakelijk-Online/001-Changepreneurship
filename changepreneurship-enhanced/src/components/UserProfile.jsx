import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { User, FileText, LogOut, ChevronDown } from 'lucide-react';

const UserProfile = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await logout();
    setIsDropdownOpen(false);
  };

  const getInitials = (username) => username ? username.charAt(0).toUpperCase() : 'U';

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        className="flex items-center gap-2 group"
      >
        {/* Avatar with glow */}
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500 to-purple-500 rounded-full blur opacity-40 group-hover:opacity-70 transition-opacity"></div>
          <div className="relative w-8 h-8 bg-gradient-to-br from-cyan-600 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold text-sm ring-1 ring-cyan-500/30">
            {getInitials(user?.username)}
          </div>
        </div>
        <span className="hidden md:block text-sm text-gray-300 group-hover:text-white transition-colors">{user?.username}</span>
        <ChevronDown className={`h-3.5 w-3.5 text-gray-500 transition-transform duration-200 ${isDropdownOpen ? 'rotate-180' : ''}`} />
      </button>

      {isDropdownOpen && (
        <div className="absolute right-0 mt-3 w-52 bg-gray-950 border border-gray-800 rounded-xl shadow-2xl shadow-black/60 z-50 overflow-hidden">
          {/* Top glow accent */}
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent"></div>

          {/* User info */}
          <div className="px-4 py-3 border-b border-gray-800">
            <p className="text-sm font-semibold text-white">{user?.username}</p>
            <p className="text-xs text-gray-500 truncate">{user?.email}</p>
          </div>

          {/* Navigation */}
          <div className="py-1">
            <button
              onClick={() => { setIsDropdownOpen(false); navigate('/profile'); }}
              className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
            >
              <User className="h-4 w-4 text-gray-600" />
              Profile Settings
            </button>
            <button
              onClick={() => { setIsDropdownOpen(false); navigate('/assessment-history'); }}
              className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
            >
              <FileText className="h-4 w-4 text-gray-600" />
              Assessment History
            </button>
          </div>

          {/* Sign out */}
          <div className="border-t border-gray-800 py-1">
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/5 transition-colors"
            >
              <LogOut className="h-4 w-4" />
              Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserProfile;

