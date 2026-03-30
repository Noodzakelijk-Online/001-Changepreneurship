import React, { useState } from "react";
import { useAuth } from "../../contexts/AuthContext";
import { TrendingUp } from "lucide-react";

const LoginForm = ({ onSwitchToRegister, onClose }) => {
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: "",
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    // Basic validation
    const newErrors = {};
    if (!formData.username.trim()) {
      newErrors.username = "Username or email is required";
    }
    if (!formData.password) {
      newErrors.password = "Password is required";
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      setIsLoading(false);
      return;
    }

    const credentials = formData.username.includes("@")
      ? { email: formData.username.trim(), password: formData.password }
      : { username: formData.username.trim(), password: formData.password };

    const result = await login(credentials);

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

      <h2 className="text-2xl font-bold text-white text-center mb-1">Welcome back</h2>
      <p className="text-gray-500 text-sm text-center mb-8">Continue your founder journey</p>

      {errors.general && (
        <div className="mb-5 p-3 bg-red-500/10 border border-red-500/30 rounded-xl">
          <p className="text-red-400 text-sm text-center">{errors.general}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="username" className="block text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wider">
            Username or Email
          </label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            className="w-full px-4 py-3 bg-black/50 border border-gray-800 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 transition-all"
            placeholder="your_username or email@example.com"
            disabled={isLoading}
          />
          {errors.username && <p className="mt-1.5 text-xs text-red-400">{errors.username}</p>}
        </div>

        <div>
          <label htmlFor="password" className="block text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wider">
            Password
          </label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            className="w-full px-4 py-3 bg-black/50 border border-gray-800 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 transition-all"
            placeholder="••••••••"
            disabled={isLoading}
          />
          {errors.password && <p className="mt-1.5 text-xs text-red-400">{errors.password}</p>}
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full mt-2 bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-400 hover:to-purple-400 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center shadow-lg shadow-cyan-500/20"
        >
          {isLoading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Signing In...
            </>
          ) : (
            'Sign In'
          )}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-gray-500">
        No account yet?{' '}
        <button onClick={onSwitchToRegister} className="text-cyan-400 hover:text-cyan-300 font-medium transition-colors">
          Create one free
        </button>
      </p>
    </div>
  );
};

export default LoginForm;
