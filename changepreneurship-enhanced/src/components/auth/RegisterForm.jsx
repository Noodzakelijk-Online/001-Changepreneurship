import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { TrendingUp } from 'lucide-react';

const RegisterForm = ({ onSwitchToLogin, onClose }) => {
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Username validation
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters long';
    }

    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long';
    } else if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = 'Password must contain at least one letter and one number';
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    const validationErrors = validateForm();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      setIsLoading(false);
      return;
    }

    const result = await register({
      username: formData.username.trim(),
      email: formData.email.trim().toLowerCase(),
      password: formData.password
    });
    
    if (result.success) {
      onClose();
    } else {
      setErrors({ general: result.error });
    }
    
    setIsLoading(false);
  };

  return (
    <div className="w-full">
      {/* Logo */}
      <div className="flex items-center justify-center gap-2 mb-8">
        <div className="relative">
          <div className="absolute inset-0 bg-cyan-500 blur-lg opacity-40"></div>
          <TrendingUp className="h-6 w-6 text-cyan-400 relative" />
        </div>
        <span className="text-lg font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
          Changepreneurship
        </span>
      </div>

      <h2 className="text-2xl font-bold text-white text-center mb-1">Start your journey</h2>
      <p className="text-gray-500 text-sm text-center mb-8">Free account — no credit card required</p>

      {errors.general && (
        <div className="mb-5 p-3 bg-red-500/10 border border-red-500/30 rounded-xl">
          <p className="text-red-400 text-sm text-center">{errors.general}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="username" className="block text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wider">Username</label>
          <input
            type="text" id="username" name="username"
            value={formData.username} onChange={handleChange}
            className="w-full px-4 py-3 bg-black/50 border border-gray-800 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 transition-all"
            placeholder="choose_a_username" disabled={isLoading}
          />
          {errors.username && <p className="mt-1.5 text-xs text-red-400">{errors.username}</p>}
        </div>

        <div>
          <label htmlFor="email" className="block text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wider">Email Address</label>
          <input
            type="email" id="email" name="email"
            value={formData.email} onChange={handleChange}
            className="w-full px-4 py-3 bg-black/50 border border-gray-800 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 transition-all"
            placeholder="email@example.com" disabled={isLoading}
          />
          {errors.email && <p className="mt-1.5 text-xs text-red-400">{errors.email}</p>}
        </div>

        <div>
          <label htmlFor="password" className="block text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wider">Password</label>
          <input
            type="password" id="password" name="password"
            value={formData.password} onChange={handleChange}
            className="w-full px-4 py-3 bg-black/50 border border-gray-800 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 transition-all"
            placeholder="••••••••" disabled={isLoading}
          />
          {errors.password
            ? <p className="mt-1.5 text-xs text-red-400">{errors.password}</p>
            : <p className="mt-1 text-xs text-gray-600">Min 8 characters, letters and numbers</p>
          }
        </div>

        <div>
          <label htmlFor="confirmPassword" className="block text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wider">Confirm Password</label>
          <input
            type="password" id="confirmPassword" name="confirmPassword"
            value={formData.confirmPassword} onChange={handleChange}
            className="w-full px-4 py-3 bg-black/50 border border-gray-800 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 transition-all"
            placeholder="••••••••" disabled={isLoading}
          />
          {errors.confirmPassword && <p className="mt-1.5 text-xs text-red-400">{errors.confirmPassword}</p>}
        </div>

        <button
          type="submit" disabled={isLoading}
          className="w-full mt-2 bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-400 hover:to-purple-400 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center shadow-lg shadow-cyan-500/20"
        >
          {isLoading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Creating Account...
            </>
          ) : 'Create Free Account'}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-gray-500">
        Already have an account?{' '}
        <button onClick={onSwitchToLogin} className="text-cyan-400 hover:text-cyan-300 font-medium transition-colors">
          Sign in
        </button>
      </p>
    </div>
  );
};

export default RegisterForm;

