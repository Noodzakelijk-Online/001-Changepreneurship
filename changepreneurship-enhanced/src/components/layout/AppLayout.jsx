/**
 * AppLayout — Sprint 8
 *
 * Full-page layout for authenticated users.
 * Replaces the old top-nav-only approach with:
 *   - Left sidebar (AppSidebar)
 *   - Main content area (children)
 *   - Mobile hamburger toggle
 *   - Slim top bar on mobile (brand + hamburger)
 *
 * Used for all pages that need the sidebar: /dashboard, /assessment/*, /profile, etc.
 * LandingPage and /login use their own layout (no sidebar).
 */
import { useState } from 'react';
import { Menu } from 'lucide-react';
import AppSidebar from './AppSidebar';

export default function AppLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-[#0a0a0f] overflow-hidden">
      {/* ── Desktop sidebar (always visible on lg+) ── */}
      <div className="hidden lg:flex flex-col">
        <AppSidebar />
      </div>

      {/* ── Mobile sidebar overlay ── */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-40 flex">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setSidebarOpen(false)}
          />
          {/* Sidebar drawer */}
          <div className="relative flex flex-col z-50">
            <AppSidebar onClose={() => setSidebarOpen(false)} />
          </div>
        </div>
      )}

      {/* ── Main column ── */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Mobile top bar */}
        <div className="lg:hidden flex items-center gap-3 px-4 py-3 border-b border-white/5 bg-[#0f0f14] shrink-0">
          <button
            onClick={() => setSidebarOpen(true)}
            className="text-slate-400 hover:text-white"
            aria-label="Open navigation"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs">C</div>
            <span className="text-sm font-semibold text-white">Changepreneurship</span>
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
