import { useState, useEffect } from 'react'
import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import NewJob from './pages/NewJob'
import JobDetail from './pages/JobDetail'
import Settings from './pages/Settings'

function App() {
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [theme, setTheme] = useState(() => localStorage.getItem('clipit_theme') || 'dark')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('clipit_theme', theme)
  }, [theme])

  // Close mobile sidebar on route navigation
  useEffect(() => {
    setMobileOpen(false)
  }, [location.pathname])

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'))
  }

  return (
    <div className="app-layout">
      {/* Mobile Backdrop Overlay */}
      <div
        className={`mobile-overlay ${mobileOpen ? 'open' : ''}`}
        onClick={() => setMobileOpen(false)}
      />

      {/* Sidebar */}
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

        <nav className="sidebar-nav">
          <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="icon">📊</span>
            Dashboard
          </NavLink>
          <NavLink to="/new" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="icon">➕</span>
            New Job
          </NavLink>
          <NavLink to="/settings" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="icon">⚙️</span>
            Settings
          </NavLink>
        </nav>

        <div style={{ padding: '12px 14px', borderTop: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            Clipit Core v1.15.0
          </div>
          <span style={{ fontSize: '10px', color: 'var(--accent)', fontWeight: 600 }}>PRO</span>
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
          <button
            type="button"
            onClick={toggleTheme}
            className="btn btn-ghost btn-sm"
            style={{ padding: '4px 8px' }}
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </header>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/new" element={<NewJob />} />
            <Route path="/job/:jobId" element={<JobDetail />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App
