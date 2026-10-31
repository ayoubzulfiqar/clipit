import { useState, useEffect } from 'react'
import { fetchSettings, updateSettings, fetchReadiness, getApiKey, setApiKey } from '../api'

const PasswordInput = ({ value, onChange, placeholder, isSet }) => {
  const [show, setShow] = useState(false)
  return (
    <div style={{ position: 'relative' }}>
      <input
        className="form-input"
        type={show ? "text" : "password"}
        placeholder={isSet ? '••••••••••••••••' : placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={{ paddingRight: '40px' }}
      />
      <button
        type="button"
        onClick={() => setShow(!show)}
        style={{
          position: 'absolute',
          right: '12px',
          top: '50%',
          transform: 'translateY(-50%)',
          background: 'none',
          border: 'none',
          color: 'var(--text-secondary)',
          cursor: 'pointer',
          fontSize: '14px',
          padding: '4px'
        }}
        title={show ? "Hide" : "Show"}
      >
        {show ? '👀' : '👁️'}
      </button>
    </div>
  )
}

function Settings() {
  const [settings, setSettings] = useState(null)
  const [readiness, setReadiness] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState('')

  // Form fields
  const [clientApiKey, setClientApiKey] = useState(getApiKey())
  const [googleKey, setGoogleKey] = useState('')
  const [pexelsKey, setPexelsKey] = useState('')
  const [hfToken, setHfToken] = useState('')
  const [nvidiaKey, setNvidiaKey] = useState('')

  useEffect(() => {
    Promise.all([
      fetchSettings().catch(() => null),
      fetchReadiness().catch(() => null),
    ]).then(([sData, rData]) => {
      if (sData) setSettings(sData)
      if (rData) setReadiness(rData)
      setLoading(false)
    })
  }, [])

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    setMsg('')
    try {
      // Save client auth key
      setApiKey(clientApiKey)

      const payload = {}
      if (googleKey) payload.google_api_key = googleKey
      if (pexelsKey) payload.pexels_api_key = pexelsKey
      if (hfToken) payload.hf_token = hfToken
      if (nvidiaKey) payload.nvidia_api_key = nvidiaKey

      if (Object.keys(payload).length > 0) {
        const updated = await updateSettings(payload)
        setSettings(updated)
      }

      setGoogleKey('')
      setPexelsKey('')
      setHfToken('')
      setNvidiaKey('')
      setMsg('✅ Settings & API keys berhasil disimpan!')
    } catch (err) {
      setMsg('❌ Gagal menyimpan: ' + err.message)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="empty-state"><div className="spinner"></div></div>

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h2>Settings</h2>
          <p>Konfigurasi API keys, akses otentikasi, dan status sistem</p>
        </div>
      </div>

      <form onSubmit={handleSave}>
        <div className="settings-grid">
          {/* API Keys */}
          <div className="settings-section">
            <h3>🔑 API Keys & Auth</h3>

            <div className="form-group">
              <label className="form-label">
                Clipit Client API Key
                {clientApiKey && <span style={{ color: 'var(--success)', marginLeft: '8px' }}>✅ Configured</span>}
              </label>
              <PasswordInput
                value={clientApiKey}
                onChange={setClientApiKey}
                placeholder="Masukkan API Key server jika server diproteksi"
                isSet={!!clientApiKey}
              />
              <p className="form-hint">Disimpan secara aman di browser lokal (localStorage) untuk otentikasi request ke backend.</p>
            </div>

            <div className="form-group">
              <label className="form-label">
                Google Gemini API Key
                {settings?.google_api_key_set && <span style={{ color: 'var(--success)', marginLeft: '8px' }}>✅ Set</span>}
              </label>
              <PasswordInput
                value={googleKey}
                onChange={setGoogleKey}
                placeholder="Paste your Gemini API key"
                isSet={settings?.google_api_key_set}
              />
              <p className="form-hint">
                <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener" style={{ color: 'var(--accent)' }}>Get free key →</a>
              </p>
            </div>

            <div className="form-group">
              <label className="form-label">
                Pexels API Key
                {settings?.pexels_api_key_set && <span style={{ color: 'var(--success)', marginLeft: '8px' }}>✅ Set</span>}
              </label>
              <PasswordInput
                value={pexelsKey}
                onChange={setPexelsKey}
                placeholder="For B-roll footage (optional)"
                isSet={settings?.pexels_api_key_set}
              />
              <p className="form-hint">Diperlukan untuk otomatisasi stock footage B-Roll</p>
            </div>

            <div className="form-group">
              <label className="form-label">
                HuggingFace Token
                {settings?.hf_token_set && <span style={{ color: 'var(--success)', marginLeft: '8px' }}>✅ Set</span>}
              </label>
              <PasswordInput
                value={hfToken}
                onChange={setHfToken}
                placeholder="For split-screen mode (optional)"
                isSet={settings?.hf_token_set}
              />
              <p className="form-hint">Diperlukan untuk speaker diarization (Pyannote 3.1)</p>
            </div>

            <div className="form-group">
              <label className="form-label">
                NVIDIA API Key
                {settings?.nvidia_api_key_set && <span style={{ color: 'var(--success)', marginLeft: '8px' }}>✅ Set</span>}
              </label>
              <PasswordInput
                value={nvidiaKey}
                onChange={setNvidiaKey}
                placeholder="For NVIDIA NIM provider (optional)"
                isSet={settings?.nvidia_api_key_set}
              />
            </div>
          </div>

          {/* System Info */}
          <div className="settings-section">
            <h3>💻 System & Diagnostics</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Server Status</span>
                <span style={{ color: readiness?.status === 'ready' ? 'var(--success)' : 'var(--accent-hover)' }}>
                  {readiness?.status === 'ready' ? '🟢 Ready' : '🟡 Degraded / Starting'}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>GPU Accelerator</span>
                <span style={{ color: (settings?.gpu_available || readiness?.checks?.gpu?.available) ? 'var(--success)' : 'var(--text-tertiary)' }}>
                  {(settings?.gpu_available || readiness?.checks?.gpu?.available) ? '✅ CUDA Active' : '⚪ CPU Mode'}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>FFmpeg Video Encoder</span>
                <span>{readiness?.checks?.video_encoder?.encoder || 'libx264'}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Storage Free Space</span>
                <span>{readiness?.checks?.storage?.free_gb ? `${readiness.checks.storage.free_gb} GB` : 'OK'}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Default AI Provider</span>
                <span>{settings?.default_ai_provider || 'gemini'}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Default Aspect Ratio</span>
                <span>{settings?.default_ratio || '9:16'}</span>
              </div>
            </div>
          </div>
        </div>

        {msg && (
          <div style={{ marginTop: '16px', fontSize: '13px', color: msg.startsWith('✅') ? 'var(--success)' : 'var(--error)' }}>
            {msg}
          </div>
        )}

        <button type="submit" className="btn btn-primary" disabled={saving} style={{ marginTop: '20px' }}>
          {saving ? <><span className="spinner"></span> Saving...</> : '💾 Save Settings'}
        </button>
      </form>
    </div>
  )
}

export default Settings
