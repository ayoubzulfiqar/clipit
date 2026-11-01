import { useState, useEffect } from 'react'

let toastListener = null

export function showToast(message, type = 'info', duration = 3500) {
  if (toastListener) {
    toastListener({ id: Date.now() + Math.random(), message, type, duration })
  }
}

export default function ToastContainer() {
  const [toasts, setToasts] = useState([])

  useEffect(() => {
    toastListener = (toast) => {
      setToasts((prev) => [...prev, toast])
      setTimeout(() => {
        setToasts((current) => current.filter((t) => t.id !== toast.id))
      }, toast.duration)
    }
    return () => {
      toastListener = null
    }
  }, [])

  if (toasts.length === 0) return null

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '24px',
        right: '24px',
        zIndex: 10000,
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
        pointerEvents: 'none',
      }}
    >
      {toasts.map((t) => {
        const bg =
          t.type === 'error'
            ? 'var(--danger, #ef4444)'
            : t.type === 'success'
            ? 'var(--success, #10b981)'
            : 'var(--accent, #6366f1)'

        return (
          <div
            key={t.id}
            style={{
              pointerEvents: 'auto',
              background: bg,
              color: '#ffffff',
              padding: '12px 18px',
              borderRadius: '10px',
              fontSize: '13px',
              fontWeight: 500,
              boxShadow: '0 10px 25px -5px rgba(0,0,0,0.3)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              animation: 'slideIn 0.2s ease',
            }}
          >
            <span>{t.type === 'error' ? '⚠️' : t.type === 'success' ? '✅' : 'ℹ️'}</span>
            <span>{t.message}</span>
          </div>
        )
      })}
    </div>
  )
}
