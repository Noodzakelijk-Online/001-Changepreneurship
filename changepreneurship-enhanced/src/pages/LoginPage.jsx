/**
 * LoginPage — Dark-themed login page matching site design system.
 * Redirects to the page the user was trying to access, or /dashboard.
 */
import React, { useState, useEffect } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { Loader2, Eye, EyeOff, Brain } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext.jsx";
import "./LoginPage.css";

const LoginPage = () => {
  const navigate   = useNavigate();
  const location   = useLocation();
  const { login, isAuthenticated, isLoading: authLoading } = useAuth();

  const from = location.state?.from || "/dashboard";

  const [credentials, setCredentials] = useState({ username: "", password: "" });
  const [showPass,    setShowPass]    = useState(false);
  const [loading,     setLoading]     = useState(false);
  const [error,       setError]       = useState(null);

  // If already authenticated, redirect immediately
  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, authLoading, from, navigate]);

  const handleChange = (e) => {
    setError(null);
    setCredentials((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!credentials.username.trim() || !credentials.password) {
      setError("Please enter your username and password.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await login(credentials);
      if (result.success) {
        navigate(from, { replace: true });
      } else {
        const msg = result.error || result.data?.message || "Invalid username or password.";
        setError(msg.includes("401") || msg.includes("unauthorized") ? "Invalid username or password." : msg);
      }
    } catch (err) {
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  if (authLoading) {
    return (
      <div className="login-page">
        <div className="login-bg" />
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh" }}>
          <Loader2 className="animate-spin" style={{ width: 32, height: 32, color: "#a855f7" }} />
        </div>
      </div>
    );
  }

  return (
    <div className="login-page">
      <div className="login-bg" />
      <div className="login-center">

        {/* Brand */}
        <div className="login-brand">
          <div className="login-logo">
            <Brain style={{ width: 28, height: 28, color: "#f97316" }} />
          </div>
          <span className="login-brand-name">Changepreneurship</span>
        </div>

        <div className="login-card">
          <h1 className="login-title">Welcome back</h1>
          <p className="login-sub">Sign in to continue your entrepreneur journey</p>

          <form onSubmit={handleSubmit} className="login-form" noValidate>
            <div className="login-field">
              <label className="login-label">Username or Email</label>
              <input
                className={`login-input ${error ? "login-input-err" : ""}`}
                type="text"
                name="username"
                autoComplete="username"
                placeholder="Enter your username"
                value={credentials.username}
                onChange={handleChange}
                disabled={loading}
              />
            </div>

            <div className="login-field">
              <label className="login-label">Password</label>
              <div className="login-pass-wrap">
                <input
                  className={`login-input ${error ? "login-input-err" : ""}`}
                  type={showPass ? "text" : "password"}
                  name="password"
                  autoComplete="current-password"
                  placeholder="Enter your password"
                  value={credentials.password}
                  onChange={handleChange}
                  disabled={loading}
                />
                <button
                  type="button"
                  className="login-eye"
                  onClick={() => setShowPass((p) => !p)}
                  tabIndex={-1}
                >
                  {showPass ? <EyeOff style={{ width: 16, height: 16 }} /> : <Eye style={{ width: 16, height: 16 }} />}
                </button>
              </div>
            </div>

            {error && (
              <div className="login-error">{error}</div>
            )}

            <button
              type="submit"
              className="login-btn"
              disabled={loading}
            >
              {loading
                ? <><Loader2 className="animate-spin" style={{ width: 16, height: 16 }} /> Signing in…</>
                : "Sign In"}
            </button>
          </form>

          <div className="login-footer">
            Don't have an account?{" "}
            <Link to="/" className="login-link">Get started on the landing page</Link>
          </div>
        </div>

        {from !== "/dashboard" && (
          <p className="login-redirect-note">
            You'll be returned to <span style={{ color: "#a855f7" }}>{from}</span> after signing in.
          </p>
        )}
      </div>
    </div>
  );
};

export default LoginPage;
