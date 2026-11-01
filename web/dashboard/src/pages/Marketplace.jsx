import { useState, useEffect } from 'react'
import {
  fetchPresets,
  createPreset,
  deletePreset,
  exportMarketplacePack,
  importMarketplacePack,
} from '../api'
import { showToast } from '../components/Toast'

export default function Marketplace() {
  const [presets, setPresets] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newPreset, setNewPreset] = useState({
    name: '',
    description: '',
    pilihan_rasio: '9:16',
    font_style: 'HORMOZI',
    keyword_palette: 'modern',
    use_sfx: true,
    semantic_emojis: true,
    normalize_audio: true,
  })
  const [importing, setImporting] = useState(false)

  const loadPresets = async () => {
    try {
      setLoading(true)
      const data = await fetchPresets()
      setPresets(data || [])
    } catch (err) {
      showToast('Failed to load presets: ' + err.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPresets()
  }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!newPreset.name.trim()) {
      showToast('Preset name is required', 'error')
      return
    }

    try {
      await createPreset({
        name: newPreset.name.trim().toLowerCase().replace(/\s+/g, '_'),
        description: newPreset.description.trim(),
        config: {
          pilihan_rasio: newPreset.pilihan_rasio,
          font_style: newPreset.font_style,
          keyword_palette: newPreset.keyword_palette,
          use_sfx: newPreset.use_sfx,
          semantic_emojis: newPreset.semantic_emojis,
          normalize_audio: newPreset.normalize_audio,
        },
      })
      showToast(`Preset '${newPreset.name}' created!`, 'success')
      setShowCreateModal(false)
      loadPresets()
    } catch (err) {
      showToast(err.message, 'error')
    }
  }

  const handleDelete = async (presetName) => {
    if (!window.confirm(`Delete preset '${presetName}'?`)) return
    try {
      await deletePreset(presetName)
      showToast(`Preset '${presetName}' deleted`, 'info')
      loadPresets()
    } catch (err) {
      showToast(err.message, 'error')
    }
  }

  const handleExportPack = async (preset) => {
    try {
      showToast(`Exporting .clipit-pack for ${preset.name}...`, 'info')
      const res = await exportMarketplacePack({
        pack_name: preset.name,
        preset_name: preset.name,
        preset_data: preset.config || {},
        description: preset.description || '',
      })
      if (res.download_url) {
        window.open(res.download_url, '_blank')
        showToast(`Exported ${res.filename} successfully!`, 'success')
      }
    } catch (err) {
      showToast('Export failed: ' + err.message, 'error')
    }
  }

  const handleFileImport = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setImporting(true)
    try {
      const res = await importMarketplacePack(file)
      showToast(`Successfully imported pack: ${res.pack_name || file.name}!`, 'success')
      loadPresets()
    } catch (err) {
      showToast('Import failed: ' + err.message, 'error')
    } finally {
      setImporting(false)
      e.target.value = ''
    }
  }

  return (
    <div style={{ padding: '24px 32px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '24px', fontWeight: 800, margin: 0 }}>🎨 Presets & Marketplace</h2>
          <p style={{ color: 'var(--text-muted)', margin: '4px 0 0', fontSize: '14px' }}>
            Browse pipeline styling presets, export portable .clipit-pack bundles, and share community templates.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <label
            className="btn btn-secondary"
            style={{ cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
          >
            <span>📥 {importing ? 'Importing...' : 'Import .clipit-pack'}</span>
            <input
              type="file"
              accept=".clipit-pack,.zip"
              style={{ display: 'none' }}
              onChange={handleFileImport}
              disabled={importing}
            />
          </label>

          <button
            type="button"
            className="btn btn-primary"
            onClick={() => setShowCreateModal(true)}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
          >
            <span>➕ Create Preset</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
          Loading community presets...
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
          {presets.map((preset) => {
            const isBuiltin = [
              'tiktok_viral',
              'youtube_shorts_clean',
              'reels_aesthetic',
              'podcast_split',
              'linkedin_square',
            ].includes(preset.name)

            const cfg = preset.config || {}

            return (
              <div
                key={preset.name}
                className="card"
                style={{
                  padding: '20px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  border: isBuiltin ? '1px solid var(--border-color)' : '1px solid var(--accent)',
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                    <h3 style={{ fontSize: '17px', fontWeight: 700, margin: 0, textTransform: 'capitalize' }}>
                      {preset.name.replace(/_/g, ' ')}
                    </h3>
                    <span
                      style={{
                        fontSize: '10px',
                        fontWeight: 700,
                        padding: '2px 6px',
                        borderRadius: '4px',
                        background: isBuiltin ? 'rgba(255,255,255,0.06)' : 'rgba(99, 102, 241, 0.15)',
                        color: isBuiltin ? 'var(--text-muted)' : 'var(--accent)',
                        textTransform: 'uppercase',
                      }}
                    >
                      {isBuiltin ? 'Built-in' : 'Custom'}
                    </span>
                  </div>

                  <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '16px', lineHeight: '1.4' }}>
                    {preset.description || 'Configured clipping pipeline profile.'}
                  </p>

                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '16px' }}>
                    <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '12px', background: 'rgba(255,255,255,0.04)', color: 'var(--text-main)' }}>
                      📐 {cfg.pilihan_rasio || '9:16'}
                    </span>
                    <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '12px', background: 'rgba(255,255,255,0.04)', color: 'var(--text-main)' }}>
                      🔤 {cfg.font_style || 'HORMOZI'}
                    </span>
                    {cfg.use_sfx && (
                      <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '12px', background: 'rgba(16, 185, 129, 0.1)', color: 'var(--success)' }}>
                        🔊 SFX Active
                      </span>
                    )}
                    {cfg.semantic_emojis && (
                      <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '12px', background: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b' }}>
                        ✨ Emojis
                      </span>
                    )}
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '8px', borderTop: '1px solid var(--border-color)', paddingTop: '14px' }}>
                  <button
                    type="button"
                    onClick={() => handleExportPack(preset)}
                    className="btn btn-secondary btn-sm"
                    style={{ flex: 1, fontSize: '12px' }}
                  >
                    📦 Export Pack
                  </button>

                  {!isBuiltin && (
                    <button
                      type="button"
                      onClick={() => handleDelete(preset.name)}
                      className="btn btn-ghost btn-sm"
                      style={{ color: 'var(--danger)', fontSize: '12px' }}
                    >
                      Delete
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Create Preset Modal */}
      {showCreateModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.65)',
            backdropFilter: 'blur(4px)',
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
          }}
          onClick={() => setShowCreateModal(false)}
        >
          <div
            className="card"
            style={{ width: '100%', maxWidth: '520px', padding: '24px' }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 style={{ fontSize: '18px', fontWeight: 800, marginTop: 0, marginBottom: '16px' }}>
              Create Custom Preset
            </h3>

            <form onSubmit={handleCreate}>
              <div style={{ marginBottom: '14px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                  Preset Name
                </label>
                <input
                  type="text"
                  placeholder="e.g. viral_storyteller"
                  value={newPreset.name}
                  onChange={(e) => setNewPreset({ ...newPreset, name: e.target.value })}
                  className="input-field"
                  style={{ width: '100%' }}
                  required
                />
              </div>

              <div style={{ marginBottom: '14px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                  Description
                </label>
                <input
                  type="text"
                  placeholder="e.g. High intensity hooks with yellow keyword highlights"
                  value={newPreset.description}
                  onChange={(e) => setNewPreset({ ...newPreset, description: e.target.value })}
                  className="input-field"
                  style={{ width: '100%' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                    Aspect Ratio
                  </label>
                  <select
                    value={newPreset.pilihan_rasio}
                    onChange={(e) => setNewPreset({ ...newPreset, pilihan_rasio: e.target.value })}
                    className="input-field"
                    style={{ width: '100%' }}
                  >
                    <option value="9:16">9:16 Portrait</option>
                    <option value="1:1">1:1 Square</option>
                    <option value="16:9">16:9 Landscape</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                    Typography Style
                  </label>
                  <select
                    value={newPreset.font_style}
                    onChange={(e) => setNewPreset({ ...newPreset, font_style: e.target.value })}
                    className="input-field"
                    style={{ width: '100%' }}
                  >
                    <option value="HORMOZI">Alex Hormozi (Bold Impact)</option>
                    <option value="DEVIN">Devin Jatho (Minimalist)</option>
                    <option value="MRBEAST">MrBeast (Dynamic Yellow)</option>
                    <option value="ALI_ABDAAL">Ali Abdaal (Clean Modern)</option>
                    <option value="NEON_CYBER">Neon Cyber (High Contrast)</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={newPreset.use_sfx}
                    onChange={(e) => setNewPreset({ ...newPreset, use_sfx: e.target.checked })}
                  />
                  <span>🔊 Enable Dynamic SFX (Whooshes, Risers, Impacts)</span>
                </label>

                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={newPreset.semantic_emojis}
                    onChange={(e) => setNewPreset({ ...newPreset, semantic_emojis: e.target.checked })}
                  />
                  <span>✨ Enable Semantic Transcript Emojis</span>
                </label>

                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={newPreset.normalize_audio}
                    onChange={(e) => setNewPreset({ ...newPreset, normalize_audio: e.target.checked })}
                  />
                  <span>🎚️ Broadcast Loudness Normalization (-14 LUFS)</span>
                </label>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowCreateModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save Preset
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
