import { useState, useEffect } from 'react'
import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import NewJob from './pages/NewJob'
import BatchStudio from './pages/BatchStudio'
import Marketplace from './pages/Marketplace'
import Calendar from './pages/Calendar'
import ToolsLab from './pages/ToolsLab'
import JobDetail from './pages/JobDetail'
import Settings from './pages/Settings'
import CommandPalette from './components/CommandPalette'
import ToastContainer from './components/Toast'

function App() {
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false)
  const [theme, setTheme] = useState(() => localStorage.getItem('clipit_theme') || 'dark')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('clipit_theme', theme)
  }, [theme])

  // Close mobile sidebar on route navigation
  useEffect(() => {
    setMobileOpen(false)
  }, [location.pathname])

  // Global Ctrl+K / Cmd+K listener
  useEffect(() => {
    const handleGlobalKey = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        setCommandPaletteOpen((prev) => !prev)
      }
    }
    window.addEventListener('keydown', handleGlobalKey)
    return () => window.removeEventListener('keydown', handleGlobalKey)
  }, [])

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'))
  }

  return (
    <div className="app-layout">
      {/* Toast Notification Container */}
      <ToastContainer />

      {/* Global Command Palette */}
      <CommandPalette
        isOpen={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
        onToggleTheme={toggleTheme}
        currentTheme={theme}
      />

      {/* Mobile Backdrop Overlay */}
      <div
        className={`mobile-overlay ${mobileOpen ? 'open' : ''}`}
        onClick={() => setMobileOpen(false)}
      />

      {/* Sidebar Navigation */}
      <aside className={`sidebar ${mobileOpen ? 'open' : ''}`}>
        <div className="sidebar-brand" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1>🎬 Clipit Studio</h1>
            <p>AI Auto-Clipper v1.15.0</p>
          </div>
          <button
            type="button"
            onClick={toggleTheme}
            className="btn btn-ghost btn-sm"
            style={{ padding: '4px 8px', fontSize: '14px' }}
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </div>

        {/* Quick Command Launcher Button */}
        <div style={{ padding: '0 12px 10px' }}>
          <button
            type="button"
            onClick={() => setCommandPaletteOpen(true)}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '8px 12px',
              borderRadius: '8px',
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-muted)',
              fontSize: '12px',
              cursor: 'pointer',
            }}
          >
            <span>⚡ Command Menu</span>
            <kbd style={{ fontSize: '10px', background: 'rgba(255,255,255,0.08)', padding: '2px 4px', borderRadius: '3px' }}>
              Ctrl+K
            </kbd>
          </button>
        </div>

        <nav className="sidebar-nav">
          <div style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--text-muted)', padding: '6px 14px 4px', fontWeight: 700, letterSpacing: '0.5px' }}>
            Production
          </div>
          <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="icon">📊</span>
            Dashboard
          </NavLink>
          <NavLink to="/new" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="icon">➕</span>
            New Clip
          </NavLink>
          <NavLink to="/batch" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="icon">📦</span>
            Batch Studio
          </NavLink>

          <div style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--text-muted)', padding: '12px 14px 4px', fontWeight: 700, letterSpacing: '0.5px' }}>
            Workstation
          </div>
          <NavLink to="/marketplace" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="icon">🎨</span>
            Presets & Packs
          </NavLink>
          <NavLink to="/calendar" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="icon">📅</span>
            Release Calendar
          </NavLink>
          <NavLink to="/tools" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="icon">🧪</span>
            AI Tools Lab
          </NavLink>

          <div style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--text-muted)', padding: '12px 14px 4px', fontWeight: 700, letterSpacing: '0.5px' }}>
            System
          </div>
          <NavLink to="/settings" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="icon">⚙️</span>
            Settings
          </NavLink>
        </nav>

        <div style={{ padding: '12px 14px', borderTop: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            Clipit Core v1.15.0
          </div>
          <span style={{ fontSize: '10px', color: 'var(--accent)', fontWeight: 700, background: 'rgba(99,102,241,0.1)', padding: '2px 6px', borderRadius: '4px' }}>
            STUDIO
          </span>
        </div>
      </aside>

      {/* Main Content Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        {/* Mobile Header Bar */}
        <header className="mobile-header">
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle navigation"
          >
            ☰ Menu
          </button>
          <span style={{ fontWeight: 800, fontSize: '14px', background: 'linear-gradient(135deg, var(--accent), #c4b5fd)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Clipit Studio
          </span>
          <div style={{ display: 'flex', gap: '6px' }}>
            <button
              type="button"
              onClick={() => setCommandPaletteOpen(true)}
              className="btn btn-ghost btn-sm"
              style={{ padding: '4px 8px' }}
              title="Command Palette"
            >
              ⚡
            </button>
            <button
              type="button"
              onClick={toggleTheme}
              className="btn btn-ghost btn-sm"
              style={{ padding: '4px 8px' }}
            >
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>
          </div>
        </header>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/new" element={<NewJob />} />
            <Route path="/batch" element={<BatchStudio />} />
            <Route path="/marketplace" element={<Marketplace />} />
            <Route path="/calendar" element={<Calendar />} />
            <Route path="/tools" element={<ToolsLab />} />
            <Route path="/job/:jobId" element={<JobDetail />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App
