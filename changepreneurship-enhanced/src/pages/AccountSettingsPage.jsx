/**
 * AccountSettingsPage — Sprint 15
 * Change username and password for the authenticated user.
 * Route: /settings/account
 */
import { useState } from 'react'
import { User, Lock, CheckCircle, AlertCircle, Loader2, Eye, EyeOff } from 'lucide-react'
import apiService from '../services/api'

// ─── Helpers ─────────────────────────────────────────────────────────────────
function Section({ title, description, icon: Icon, children }) {
  return (
    <div className="bg-white/3 border border-white/5 rounded-xl p-6">
      <div className="flex items-start gap-3 mb-6">
        <div className="p-2 bg-white/5 rounded-lg">
          <Icon className="h-5 w-5 text-slate-300" />
        </div>
        <div>
          <h2 className="text-base font-semibold text-white">{title}</h2>
          <p className="text-xs text-slate-500 mt-0.5">{description}</p>
        </div>
      </div>
      {children}
    </div>
  )
}

function Alert({ type, message }) {
  if (!message) return null
  const isError = type === 'error'
  return (
    <div className={`flex items-center gap-2 p-3 rounded-lg text-sm ${
      isError ? 'bg-red-500/10 border border-red-500/20 text-red-400' : 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400'
    }`}>
      {isError ? <AlertCircle className="h-4 w-4 shrink-0" /> : <CheckCircle className="h-4 w-4 shrink-0" />}
      {message}
    </div>
  )
}

function PasswordInput({ id, label, value, onChange, placeholder }) {
  const [visible, setVisible] = useState(false)
  return (
    <div>
      <label htmlFor={id} className="block text-xs text-slate-400 mb-1.5">{label}</label>
      <div className="relative">
        <input
          id={id}
          type={visible ? 'text' : 'password'}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 pr-10 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-white/20"
        />
        <button
          type="button"
          onClick={() => setVisible(v => !v)}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
        >
          {visible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
        </button>
      </div>
    </div>
  )
}

// ─── Change Username ──────────────────────────────────────────────────────────
function ChangeUsernameForm() {
  const [username, setUsername] = useState('')
  const [status, setStatus] = useState(null)   // { type: 'error'|'success', message }
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setStatus(null)
    setLoading(true)
    try {
      const res = await apiService.request('/v1/users/me', {
        method: 'PATCH',
        body: JSON.stringify({ username: username.trim() }),
      })
      if (res.success) {
        setStatus({ type: 'success', message: 'Username updated successfully.' })
        setUsername('')
      } else {
        setStatus({ type: 'error', message: res.data?.error || res.error || 'Failed to update username.' })
      }
    } catch {
      setStatus({ type: 'error', message: 'Network error. Please try again.' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="new-username" className="block text-xs text-slate-400 mb-1.5">New username</label>
        <input
          id="new-username"
          type="text"
          value={username}
          onChange={e => setUsername(e.target.value)}
          placeholder="Enter new username"
          autoComplete="username"
          className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-white/20"
        />
        <p className="text-xs text-slate-600 mt-1.5">Minimum 3 characters.</p>
      </div>

      <Alert type={status?.type} message={status?.message} />

      <button
        type="submit"
        disabled={loading || !username.trim()}
        className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/15 disabled:opacity-40 disabled:cursor-not-allowed rounded-lg text-sm text-white font-medium transition-colors"
      >
        {loading && <Loader2 className="h-4 w-4 animate-spin" />}
        Save Username
      </button>
    </form>
  )
}

// ─── Change Password ──────────────────────────────────────────────────────────
function ChangePasswordForm() {
  const [form, setForm] = useState({ current: '', next: '', confirm: '' })
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)

  function setField(key) {
    return e => setForm(f => ({ ...f, [key]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setStatus(null)

    if (form.next !== form.confirm) {
      setStatus({ type: 'error', message: 'New passwords do not match.' })
      return
    }

    setLoading(true)
    try {
      const res = await apiService.request('/v1/auth/change-password', {
        method: 'POST',
        body: JSON.stringify({ current_password: form.current, new_password: form.next }),
      })
      if (res.success) {
        setStatus({ type: 'success', message: 'Password changed successfully.' })
        setForm({ current: '', next: '', confirm: '' })
      } else {
        setStatus({ type: 'error', message: res.data?.error || res.error || 'Failed to change password.' })
      }
    } catch {
      setStatus({ type: 'error', message: 'Network error. Please try again.' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <PasswordInput
        id="current-password"
        label="Current password"
        value={form.current}
        onChange={setField('current')}
        placeholder="Your current password"
      />
      <PasswordInput
        id="new-password"
        label="New password"
        value={form.next}
        onChange={setField('next')}
        placeholder="At least 12 characters"
      />
      <PasswordInput
        id="confirm-password"
        label="Confirm new password"
        value={form.confirm}
        onChange={setField('confirm')}
        placeholder="Repeat new password"
      />
      <p className="text-xs text-slate-600">Password must be at least 12 characters long.</p>

      <Alert type={status?.type} message={status?.message} />

      <button
        type="submit"
        disabled={loading || !form.current || !form.next || !form.confirm}
        className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/15 disabled:opacity-40 disabled:cursor-not-allowed rounded-lg text-sm text-white font-medium transition-colors"
      >
        {loading && <Loader2 className="h-4 w-4 animate-spin" />}
        Change Password
      </button>
    </form>
  )
}

// ─── Page ─────────────────────────────────────────────────────────────────────
export default function AccountSettingsPage() {
  return (
    <div className="min-h-screen bg-[#0a0a0f] px-4 py-8 sm:px-6 lg:px-8">
      <div className="max-w-xl mx-auto space-y-6">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Account Settings</h1>
          <p className="text-sm text-slate-500 mt-1">Manage your credentials.</p>
        </div>

        <Section
          title="Username"
          description="Change the name shown across the platform."
          icon={User}
        >
          <ChangeUsernameForm />
        </Section>

        <Section
          title="Password"
          description="Update your login password. You'll need your current password to proceed."
          icon={Lock}
        >
          <ChangePasswordForm />
        </Section>
      </div>
    </div>
  )
}
