import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export default function CommandPalette({ isOpen, onClose, onToggleTheme, currentTheme }) {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)

  const commands = [
    { id: 'dashboard', label: '📊 Go to Dashboard', path: '/', category: 'Navigation' },
    { id: 'new', label: '➕ New Single Clip', path: '/new', category: 'Creation' },
    { id: 'batch', label: '📦 Batch Studio (Bulk Ingest)', path: '/batch', category: 'Creation' },
    { id: 'marketplace', label: '🎨 Presets & Marketplace Packs', path: '/marketplace', category: 'Studio' },
    { id: 'calendar', label: '📅 Social Release Calendar', path: '/calendar', category: 'Studio' },
    { id: 'tools', label: '🧪 AI Tools Lab (Vision / Copyright / Chapters)', path: '/tools', category: 'Studio' },
    { id: 'settings', label: '⚙️ Settings & System Readiness', path: '/settings', category: 'System' },
    {
      id: 'theme',
      label: `🌓 Switch to ${currentTheme === 'dark' ? 'Light' : 'Dark'} Mode`,
      action: onToggleTheme,
      category: 'Preferences',
    },
    {
      id: 'docs',
      label: '📖 View API Docs (Swagger)',
      action: () => window.open('/docs', '_blank'),
      category: 'External',
    },
  ]

  const filtered = commands.filter((cmd) =>
    cmd.label.toLowerCase().includes(query.toLowerCase()) ||
    cmd.category.toLowerCase().includes(query.toLowerCase())
  )

  useEffect(() => {
    setSelectedIndex(0)
  }, [query])

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isOpen) return
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIndex((prev) => (prev + 1) % (filtered.length || 1))
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIndex((prev) => (prev - 1 + filtered.length) % (filtered.length || 1))
      } else if (e.key === 'Enter') {
        e.preventDefault()
        const selected = filtered[selectedIndex]
        if (selected) {
          execute(selected)
        }
      } else if (e.key === 'Escape') {
        onClose()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, filtered, selectedIndex])

  const execute = (cmd) => {
    onClose()
    if (cmd.path) {
      navigate(cmd.path)
    } else if (cmd.action) {
      cmd.action()
    }
  }

  if (!isOpen) return null

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.65)',
        backdropFilter: 'blur(4px)',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '15vh',
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '560px',
          background: 'var(--bg-card, #1e293b)',
          border: '1px solid var(--border-color, #334155)',
          borderRadius: '16px',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', alignItems: 'center', padding: '14px 18px', borderBottom: '1px solid var(--border-color)' }}>
          <span style={{ marginRight: '10px', fontSize: '18px' }}>⚡</span>
          <input
            autoFocus
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a command or jump to workspace..."
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              fontSize: '15px',
              color: 'var(--text-main, #fff)',
            }}
          />
          <kbd
            style={{
              fontSize: '11px',
              padding: '2px 6px',
              borderRadius: '4px',
              background: 'rgba(255,255,255,0.1)',
              color: 'var(--text-muted)',
            }}
          >
            ESC
          </kbd>
        </div>

        <div style={{ maxHeight: '340px', overflowY: 'auto', padding: '8px' }}>
          {filtered.length === 0 ? (
            <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>
              No matching commands
            </div>
          ) : (
            filtered.map((cmd, idx) => (
              <div
                key={cmd.id}
                onClick={() => execute(cmd)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px 14px',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  background: idx === selectedIndex ? 'var(--accent, #6366f1)' : 'transparent',
                  color: idx === selectedIndex ? '#fff' : 'var(--text-main)',
                  transition: 'background 0.1s ease',
                }}
                onMouseEnter={() => setSelectedIndex(idx)}
              >
                <span style={{ fontSize: '14px', fontWeight: 500 }}>{cmd.label}</span>
                <span
                  style={{
                    fontSize: '11px',
                    opacity: 0.7,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                  }}
                >
                  {cmd.category}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
