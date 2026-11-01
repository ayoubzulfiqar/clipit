import { useState, useEffect } from 'react'
import {
  scoreThumbnail,
  checkCopyright,
  generateChapters,
  fetchReadiness,
  fetchJobs,
} from '../api'
import { showToast } from '../components/Toast'

export default function ToolsLab() {
  const [activeTab, setActiveTab] = useState('vision')

  // Vision State
  const [visionFile, setVisionFile] = useState(null)
  const [visionPreview, setVisionPreview] = useState(null)
  const [visionResult, setVisionResult] = useState(null)
  const [visionLoading, setVisionLoading] = useState(false)

  // Copyright State
  const [copyrightText, setCopyrightText] = useState('')
  const [hasCommercialBgm, setHasCommercialBgm] = useState(false)
  const [copyrightDuration, setCopyrightDuration] = useState(30)
  const [copyrightResult, setCopyrightResult] = useState(null)
  const [copyrightLoading, setCopyrightLoading] = useState(false)

  // Chapters State
  const [chaptersTitle, setChaptersTitle] = useState('')
  const [chaptersSummary, setChaptersSummary] = useState('')
  const [jobs, setJobs] = useState([])
  const [selectedJobId, setSelectedJobId] = useState('')
  const [chaptersResult, setChaptersResult] = useState(null)
  const [chaptersLoading, setChaptersLoading] = useState(false)

  // Diagnostics State
  const [readiness, setReadiness] = useState(null)
  const [diagLoading, setDiagLoading] = useState(false)

  useEffect(() => {
    fetchJobs({ limit: 10 })
      .then((data) => setJobs(data.jobs || data || []))
      .catch((err) => console.error('Failed to load jobs:', err))
  }, [])

  const handleVisionScore = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setVisionFile(file)
    setVisionPreview(URL.createObjectURL(file))
    setVisionLoading(true)
    try {
      const res = await scoreThumbnail(file)
      setVisionResult(res)
      showToast('Thumbnail scored successfully!', 'success')
    } catch (err) {
      showToast(err.message, 'error')
    } finally {
      setVisionLoading(false)
    }
  }

  const handleCopyrightAudit = async (e) => {
    e.preventDefault()
    if (!copyrightText.trim()) {
      showToast('Please enter transcript text to audit', 'error')
      return
    }
    setCopyrightLoading(true)
    try {
      const res = await checkCopyright({
        transcript: copyrightText,
        has_commercial_bgm: hasCommercialBgm,
        duration: parseFloat(copyrightDuration),
      })
      setCopyrightResult(res)
      showToast(`Copyright audit complete: ${res.risk_level.toUpperCase()} risk`, 'info')
    } catch (err) {
      showToast(err.message, 'error')
    } finally {
      setCopyrightLoading(false)
    }
  }

  const handleChaptersGenerate = async (e) => {
    e.preventDefault()
    setChaptersLoading(true)
    try {
      const res = await generateChapters({
        job_id: selectedJobId || undefined,
        title: chaptersTitle || 'Episode Highlights',
        summary: chaptersSummary || '',
      })
      setChaptersResult(res)
      showToast('Chapters & show notes generated!', 'success')
    } catch (err) {
      showToast(err.message, 'error')
    } finally {
      setChaptersLoading(false)
    }
  }

  const handleRunDiagnostics = async () => {
    setDiagLoading(true)
    try {
      const data = await fetchReadiness()
      setReadiness(data)
      showToast('System diagnostics refreshed', 'success')
    } catch (err) {
      showToast('Diagnostics failed: ' + err.message, 'error')
    } finally {
      setDiagLoading(false)
    }
  }

  return (
    <div style={{ padding: '24px 32px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '24px', fontWeight: 800, margin: 0 }}>🧪 AI Tools Lab</h2>
        <p style={{ color: 'var(--text-muted)', margin: '4px 0 0', fontSize: '14px' }}>
          Deep multimodal vision, copyright risk auditing, show notes generation, and hardware diagnostics.
        </p>
      </div>

      {/* Navigation Tabs */}
      <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-color)', marginBottom: '24px' }}>
        {[
          { id: 'vision', label: '📸 Thumbnail Vision Scorer' },
          { id: 'copyright', label: '🛡️ Copyright & Content ID' },
          { id: 'chapters', label: '📌 Auto-Chapters & SEO' },
          { id: 'diagnostics', label: '⚡ Hardware Diagnostics' },
        ].map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '10px 18px',
              fontSize: '13px',
              fontWeight: 600,
              border: 'none',
              background: 'transparent',
              color: activeTab === tab.id ? 'var(--accent)' : 'var(--text-muted)',
              borderBottom: activeTab === tab.id ? '2px solid var(--accent)' : '2px solid transparent',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab 1: Vision Scorer */}
      {activeTab === 'vision' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: '24px' }}>
          <div className="card" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 700, margin: '0 0 16px' }}>Upload Frame or Thumbnail</h3>
            <label
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                border: '2px dashed var(--border-color)',
                borderRadius: '12px',
                padding: '40px 20px',
                cursor: 'pointer',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: '36px', marginBottom: '10px' }}>🖼️</div>
              <span style={{ fontSize: '14px', fontWeight: 600 }}>Click to select an image (JPG, PNG, WebP)</span>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Evaluates sharpness, contrast, exposure, and clickability.
              </span>
              <input type="file" accept="image/*" onChange={handleVisionScore} style={{ display: 'none' }} />
            </label>

            {visionPreview && (
              <div style={{ marginTop: '20px', textAlign: 'center' }}>
                <img
                  src={visionPreview}
                  alt="Preview"
                  style={{ maxHeight: '240px', borderRadius: '8px', maxWidth: '100%', objectFit: 'contain' }}
                />
              </div>
            )}
          </div>

          <div className="card" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 700, margin: '0 0 16px' }}>Multimodal Analysis Results</h3>
            {visionLoading ? (
              <div style={{ padding: '40px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
                Analyzing pixel gradients and spatial frequency...
              </div>
            ) : !visionResult ? (
              <div style={{ padding: '40px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
                Upload an image on the left to view scores.
              </div>
            ) : (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
                  <div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      Composite Virality Score
                    </div>
                    <div style={{ fontSize: '32px', fontWeight: 800, color: 'var(--accent)' }}>
                      {visionResult.composite_score} / 100
                    </div>
                  </div>
                  {visionResult.is_blurry && (
                    <span style={{ padding: '4px 10px', borderRadius: '6px', background: 'rgba(239,68,68,0.15)', color: 'var(--danger)', fontSize: '12px', fontWeight: 700 }}>
                      ⚠️ Motion Blur Detected
                    </span>
                  )}
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                      <span>Sharpness (Laplacian Variance)</span>
                      <span style={{ fontWeight: 600 }}>{visionResult.sharpness} / 100</span>
                    </div>
                    <div style={{ height: '6px', background: 'var(--border-color)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${visionResult.sharpness}%`, background: 'var(--success)' }} />
                    </div>
                  </div>

                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                      <span>Contrast & Dynamic Range</span>
                      <span style={{ fontWeight: 600 }}>{visionResult.contrast} / 100</span>
                    </div>
                    <div style={{ height: '6px', background: 'var(--border-color)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${visionResult.contrast}%`, background: '#3b82f6' }} />
                    </div>
                  </div>

                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                      <span>Exposure & Brightness Balance</span>
                      <span style={{ fontWeight: 600 }}>{visionResult.brightness} / 100</span>
                    </div>
                    <div style={{ height: '6px', background: 'var(--border-color)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${visionResult.brightness}%`, background: '#f59e0b' }} />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Copyright Auditor */}
      {activeTab === 'copyright' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: '24px' }}>
          <div className="card" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 700, margin: '0 0 16px' }}>Audit Content ID & Copyright Signals</h3>
            <form onSubmit={handleCopyrightAudit}>
              <div style={{ marginBottom: '14px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                  Transcript or Lyric Text
                </label>
                <textarea
                  rows={6}
                  value={copyrightText}
                  onChange={(e) => setCopyrightText(e.target.value)}
                  placeholder="Paste video speech transcript or song titles to audit..."
                  className="input-field"
                  style={{ width: '100%', resize: 'vertical' }}
                  required
                />
              </div>

              <div style={{ marginBottom: '14px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={hasCommercialBgm}
                    onChange={(e) => setHasCommercialBgm(e.target.checked)}
                  />
                  <span>Includes Unmodified Commercial Background Music</span>
                </label>
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                  Segment Continuous Duration: {copyrightDuration}s
                </label>
                <input
                  type="range"
                  min="5"
                  max="120"
                  value={copyrightDuration}
                  onChange={(e) => setCopyrightDuration(e.target.value)}
                  style={{ width: '100%' }}
                />
              </div>

              <button type="submit" disabled={copyrightLoading} className="btn btn-primary" style={{ width: '100%' }}>
                {copyrightLoading ? 'Scanning...' : '🛡️ Analyze Copyright Risk'}
              </button>
            </form>
          </div>

          <div className="card" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 700, margin: '0 0 16px' }}>Safety Audit & Fair-Use Recommendations</h3>
            {!copyrightResult ? (
              <div style={{ padding: '40px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
                Submit a transcript on the left to audit.
              </div>
            ) : (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <span
                    style={{
                      fontSize: '12px',
                      fontWeight: 800,
                      textTransform: 'uppercase',
                      padding: '4px 12px',
                      borderRadius: '12px',
                      background:
                        copyrightResult.risk_level === 'low'
                          ? 'rgba(16,185,129,0.15)'
                          : copyrightResult.risk_level === 'high'
                          ? 'rgba(239,68,68,0.15)'
                          : 'rgba(245,158,11,0.15)',
                      color:
                        copyrightResult.risk_level === 'low'
                          ? 'var(--success)'
                          : copyrightResult.risk_level === 'high'
                          ? 'var(--danger)'
                          : '#f59e0b',
                    }}
                  >
                    Risk Level: {copyrightResult.risk_level} ({copyrightResult.risk_score}/100)
                  </span>

                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    Monetization Safe: {copyrightResult.is_safe_for_monetization ? '✅ Yes' : '⚠️ No'}
                  </span>
                </div>

                {copyrightResult.flags && copyrightResult.flags.length > 0 && (
                  <div style={{ marginBottom: '16px' }}>
                    <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                      Detected Signals:
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {copyrightResult.flags.map((f, idx) => (
                        <span key={idx} style={{ fontSize: '11px', background: 'rgba(255,255,255,0.06)', padding: '2px 8px', borderRadius: '4px' }}>
                          🚩 {f}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px' }}>
                    Recommended Fair-Use Transformations:
                  </div>
                  {copyrightResult.recommended_transforms.length === 0 ? (
                    <div style={{ fontSize: '13px', color: 'var(--success)' }}>
                      ✅ No transformations required. Content appears original!
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {copyrightResult.recommended_transforms.map((t, idx) => (
                        <div key={idx} style={{ padding: '8px 12px', borderRadius: '6px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', fontSize: '12px' }}>
                          <span style={{ fontWeight: 700, color: 'var(--accent)' }}>{t.type}</span>: {t.rationale}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 3: Auto-Chapters */}
      {activeTab === 'chapters' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: '24px' }}>
          <div className="card" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 700, margin: '0 0 16px' }}>Generate YouTube Chapters & Show Notes</h3>
            <form onSubmit={handleChaptersGenerate}>
              <div style={{ marginBottom: '14px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                  Source Job (Optional)
                </label>
                <select
                  value={selectedJobId}
                  onChange={(e) => setSelectedJobId(e.target.value)}
                  className="input-field"
                  style={{ width: '100%' }}
                >
                  <option value="">Select a job (or use manual title)</option>
                  {jobs.map((j) => (
                    <option key={j.id} value={j.id}>
                      {j.id} ({j.clips?.length || 0} clips)
                    </option>
                  ))}
                </select>
              </div>

              <div style={{ marginBottom: '14px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                  Video Title
                </label>
                <input
                  type="text"
                  placeholder="e.g. How to Scale AI Pipelines"
                  value={chaptersTitle}
                  onChange={(e) => setChaptersTitle(e.target.value)}
                  className="input-field"
                  style={{ width: '100%' }}
                />
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                  Overview / Summary
                </label>
                <textarea
                  rows={3}
                  placeholder="Brief synopsis of the episode..."
                  value={chaptersSummary}
                  onChange={(e) => setChaptersSummary(e.target.value)}
                  className="input-field"
                  style={{ width: '100%' }}
                />
              </div>

              <button type="submit" disabled={chaptersLoading} className="btn btn-primary" style={{ width: '100%' }}>
                {chaptersLoading ? 'Generating...' : '📌 Generate Timestamps & Notes'}
              </button>
            </form>
          </div>

          <div className="card" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 700, margin: '0 0 16px' }}>Generated Markdown & Chapters</h3>
            {!chaptersResult ? (
              <div style={{ padding: '40px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
                Configure parameters on the left to generate.
              </div>
            ) : (
              <div>
                <div style={{ marginBottom: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <span style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                      YouTube Description Timestamps
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        navigator.clipboard.writeText(chaptersResult.youtube_block)
                        showToast('Copied YouTube timestamps!', 'success')
                      }}
                      className="btn btn-secondary btn-sm"
                      style={{ fontSize: '11px', padding: '2px 8px' }}
                    >
                      📋 Copy
                    </button>
                  </div>
                  <pre
                    style={{
                      background: 'rgba(0,0,0,0.3)',
                      padding: '12px',
                      borderRadius: '8px',
                      fontSize: '12px',
                      whiteSpace: 'pre-wrap',
                      fontFamily: 'monospace',
                    }}
                  >
                    {chaptersResult.youtube_block}
                  </pre>
                </div>

                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <span style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                      Markdown Show Notes
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        navigator.clipboard.writeText(chaptersResult.show_notes_markdown)
                        showToast('Copied markdown show notes!', 'success')
                      }}
                      className="btn btn-secondary btn-sm"
                      style={{ fontSize: '11px', padding: '2px 8px' }}
                    >
                      📋 Copy
                    </button>
                  </div>
                  <textarea
                    readOnly
                    rows={8}
                    value={chaptersResult.show_notes_markdown}
                    className="input-field"
                    style={{ width: '100%', fontSize: '12px', fontFamily: 'monospace' }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 4: Diagnostics */}
      {activeTab === 'diagnostics' && (
        <div className="card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <div>
              <h3 style={{ fontSize: '16px', fontWeight: 700, margin: 0 }}>System Readiness & Hardware Probe</h3>
              <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: '4px 0 0' }}>
                Validates FFmpeg codecs, hardware acceleration, disk space, and worker queue health.
              </p>
            </div>
            <button
              type="button"
              onClick={handleRunDiagnostics}
              disabled={diagLoading}
              className="btn btn-primary btn-sm"
            >
              {diagLoading ? 'Probing...' : '🔄 Run Probe'}
            </button>
          </div>

          {!readiness ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
              Click "Run Probe" to test system health.
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
              <div style={{ padding: '16px', borderRadius: '10px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Overall Status</div>
                <div style={{ fontSize: '20px', fontWeight: 800, marginTop: '4px', color: readiness.ready ? 'var(--success)' : 'var(--danger)' }}>
                  {readiness.ready ? '✅ System Ready' : '⚠️ Degraded'}
                </div>
              </div>

              <div style={{ padding: '16px', borderRadius: '10px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Video Encoder</div>
                <div style={{ fontSize: '16px', fontWeight: 700, marginTop: '4px' }}>
                  {readiness.encoder?.name || 'libx264 (CPU)'}
                </div>
              </div>

              <div style={{ padding: '16px', borderRadius: '10px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Storage</div>
                <div style={{ fontSize: '16px', fontWeight: 700, marginTop: '4px' }}>
                  {readiness.storage?.free_gb ? `${readiness.storage.free_gb} GB Free` : 'Writable'}
                </div>
              </div>

              <div style={{ padding: '16px', borderRadius: '10px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Worker Queue</div>
                <div style={{ fontSize: '16px', fontWeight: 700, marginTop: '4px' }}>
                  Active Tasks: {readiness.queue?.queued_jobs ?? 0}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
