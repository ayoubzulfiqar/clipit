import { useState, useEffect, useRef } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import {
  fetchJob,
  deleteJob,
  cancelJob,
  retryJob,
  updateJobTags,
  createSSEConnection,
  getZipDownloadUrl,
} from '../api'

const STEPS = [
  { key: 'download', label: 'Download' },
  { key: 'transcribe', label: 'Transcribe' },
  { key: 'analyze', label: 'AI Analysis' },
  { key: 'metadata', label: 'Metadata' },
  { key: 'render', label: 'Render' },
  { key: 'done', label: 'Done' },
]

function JobDetail() {
  const { jobId } = useParams()
  const navigate = useNavigate()
  const [job, setJob] = useState(null)
  const [loading, setLoading] = useState(true)
  const [tagInput, setTagInput] = useState('')
  const [activeRatio, setActiveRatio] = useState('9:16')
  const [busyAction, setBusyAction] = useState(false)
  const [expandedTranscript, setExpandedTranscript] = useState({})
  const videoRefs = useRef({})

  const reload = async () => {
    try {
      const data = await fetchJob(jobId)
      setJob(data)
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    let sse = null

    const load = async () => {
      try {
        const data = await fetchJob(jobId)
        setJob(data)

        const terminal = ['completed', 'failed', 'cancelled']
        if (!terminal.includes(data.status)) {
          sse = createSSEConnection(jobId, (event) => {
            if (event.type === 'completed') {
              fetchJob(jobId).then(setJob)
            } else if (event.type === 'progress') {
              setJob(prev => prev ? { ...prev, status: event.status, progress: event.progress, error: event.error } : prev)
            }
          })
        }
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    load()
    return () => { if (sse) sse.close() }
  }, [jobId])

  useEffect(() => {
    if (!job) return
    const terminal = ['completed', 'failed', 'cancelled']
    if (terminal.includes(job.status)) return

    const interval = setInterval(reload, 3000)
    return () => clearInterval(interval)
  }, [jobId, job?.status])

  const handleCancel = async () => {
    if (busyAction) return
    setBusyAction(true)
    try {
      await cancelJob(jobId)
      await reload()
    } catch (err) {
      alert(`Gagal membatalkan job: ${err.message}`)
    } finally {
      setBusyAction(false)
    }
  }

  const handleRetry = async () => {
    if (busyAction) return
    setBusyAction(true)
    try {
      await retryJob(jobId)
      await reload()
    } catch (err) {
      alert(`Gagal me-retry job: ${err.message}`)
    } finally {
      setBusyAction(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Hapus job dan semua file output?')) return
    try {
      await deleteJob(jobId)
      navigate('/')
    } catch (err) {
      alert(`Gagal menghapus: ${err.message}`)
    }
  }

  const handleAddTag = async (e) => {
    e.preventDefault()
    if (!tagInput.trim()) return
    const newTags = Array.from(new Set([...(job.tags || []), tagInput.trim().toLowerCase()]))
    try {
      await updateJobTags(jobId, newTags)
      setTagInput('')
      await reload()
    } catch (err) {
      alert(`Gagal update tag: ${err.message}`)
    }
  }

  const handleRemoveTag = async (tagToRemove) => {
    const newTags = (job.tags || []).filter(t => t !== tagToRemove)
    try {
      await updateJobTags(jobId, newTags)
      await reload()
    } catch (err) {
      alert(`Gagal menghapus tag: ${err.message}`)
    }
  }

  const toggleTranscript = (clipIdx) => {
    setExpandedTranscript(prev => ({
      ...prev,
      [clipIdx]: !prev[clipIdx],
    }))
  }

  const seekVideo = (clipIdx, seconds) => {
    const vid = videoRefs.current[clipIdx]
    if (vid) {
      vid.currentTime = Math.max(0, seconds)
      vid.play()
    }
  }

  if (loading) return <div className="empty-state"><div className="spinner"></div></div>
  if (!job) return <div className="empty-state"><h3>Job not found</h3></div>

  const currentStep = job.progress?.step || ''
  const percent = job.progress?.percent || 0
  const isTerminal = ['completed', 'failed', 'cancelled'].includes(job.status)

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h2>Job #{job.id}</h2>
          <p>{job.url || job.upload_filename || 'Unknown source'}</p>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', alignItems: 'center' }}>
          <span className={`badge badge-${job.status}`}>{job.status}</span>

          {job.status === 'completed' && (
            <a href={getZipDownloadUrl(job.id)} download={`clipit_${job.id}.zip`} className="btn btn-primary btn-sm">
              📦 Download All (.ZIP)
            </a>
          )}

          {!isTerminal && (
            <button onClick={handleCancel} disabled={busyAction} className="btn btn-danger btn-sm">
              ⏹ Cancel
            </button>
          )}

          {['failed', 'cancelled'].includes(job.status) && (
            <button onClick={handleRetry} disabled={busyAction} className="btn btn-secondary btn-sm">
              🔄 Retry
            </button>
          )}

          <Link to="/new" state={{ reuseJob: job }} className="btn btn-secondary btn-sm">🔁 Clone & Rerun</Link>
          <button onClick={handleDelete} className="btn btn-ghost btn-sm" style={{ color: 'var(--error)' }}>🗑 Delete</button>
          <Link to="/" className="btn btn-ghost btn-sm">← Back</Link>
        </div>
      </div>

      {/* Tags Bar */}
      <div className="card" style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-tertiary)' }}>TAGS:</span>
          {(!job.tags || job.tags.length === 0) && (
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Belum ada tag</span>
          )}
          {job.tags?.map((t, idx) => (
            <span key={idx} style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', background: 'var(--bg-tertiary)', padding: '2px 8px', borderRadius: '12px', fontSize: '12px' }}>
              #{t}
              <button
                type="button"
                onClick={() => handleRemoveTag(t)}
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: 0, fontSize: '12px' }}
              >
                ×
              </button>
            </span>
          ))}
        </div>

        <form onSubmit={handleAddTag} style={{ display: 'flex', gap: '6px' }}>
          <input
            type="text"
            className="form-input"
            style={{ width: '130px', padding: '4px 8px', fontSize: '12px' }}
            placeholder="+ Tag..."
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
          />
          <button type="submit" className="btn btn-secondary btn-sm">Add</button>
        </form>
      </div>

      {/* Progress Bar */}
      {!isTerminal && (
        <div className="card" style={{ marginBottom: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '13px', fontWeight: 600 }}>Progress</span>
            <span style={{ fontSize: '13px', color: 'var(--accent-hover)' }}>{Math.round(percent)}%</span>
          </div>
          <div className="progress-bar-bg">
            <div className="progress-bar-fill" style={{ width: `${percent}%` }}></div>
          </div>
          {job.progress?.message && (
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '10px' }}>
              {job.progress.message}
            </p>
          )}
          <div className="progress-steps" style={{ marginTop: '14px' }}>
            {STEPS.map(s => {
              const stepIdx = STEPS.findIndex(x => x.key === s.key)
              const currentIdx = STEPS.findIndex(x => x.key === currentStep)
              let cls = ''
              if (stepIdx < currentIdx) cls = 'done'
              else if (stepIdx === currentIdx) cls = 'active'
              return (
                <div key={s.key} className={`progress-step ${cls}`}>
                  <span className="step-dot"></span>
                  {s.label}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Error Notice */}
      {job.error && (
        <div className="card" style={{ marginBottom: '16px', borderColor: 'rgba(239,68,68,0.2)' }}>
          <h3 style={{ color: 'var(--error)', fontSize: '14px', marginBottom: '8px' }}>❌ Error</h3>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{job.error}</p>
        </div>
      )}

      {/* Multi-Layout Aspect Ratio Preview Selector */}
      {job.clips && job.clips.length > 0 && (
        <div className="card" style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
          <div>
            <h4 style={{ margin: 0, fontSize: '13px', fontWeight: 700 }}>📱 Multi-Layout Previewer</h4>
            <p style={{ margin: 0, fontSize: '11px', color: 'var(--text-secondary)' }}>Simulasi framing platform (TikTok 9:16, Instagram/X 1:1, YouTube 16:9)</p>
          </div>
          <div style={{ display: 'flex', gap: '6px' }}>
            {[
              { ratio: '9:16', label: '9:16 Mobile' },
              { ratio: '1:1', label: '1:1 Square' },
              { ratio: '16:9', label: '16:9 Wide' },
            ].map(r => (
              <button
                key={r.ratio}
                type="button"
                className={`btn btn-sm ${activeRatio === r.ratio ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActiveRatio(r.ratio)}
              >
                {r.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Generated Clips */}
      {job.clips && job.clips.length > 0 && (
        <>
          <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>
            🎞️ Generated Clips ({job.clips.length})
          </h3>
          <div className="clip-grid">
            {job.clips.map((clip, i) => (
              <div key={i} className="clip-card">
                <div style={{
                  display: 'flex',
                  justifyContent: 'center',
                  background: '#000',
                  borderRadius: '8px 8px 0 0',
                  overflow: 'hidden',
                  aspectRatio: activeRatio === '9:16' ? '9/16' : activeRatio === '1:1' ? '1/1' : '16/9',
                  maxHeight: '480px',
                }}>
                  <video
                    ref={el => { videoRefs.current[i] = el }}
                    style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                    controls
                    preload="metadata"
                    src={clip.download_url}
                  />
                </div>
                <div className="clip-body">
                  <div className="clip-title">{clip.title || clip.title_en || `Clip ${clip.rank}`}</div>
                  <div className="clip-stats">
                    {clip.viral_score && <span className="viral-score">🔥 {clip.viral_score}</span>}
                    {clip.duration && <span>⏱️ {Math.round(clip.duration)}s</span>}
                    <span>Rank #{clip.rank}</span>
                  </div>

                  {/* Virality Factor Breakdown */}
                  {clip.virality_factors && (
                    <div style={{ margin: '8px 0', padding: '6px 8px', background: 'var(--bg-tertiary)', borderRadius: '6px', fontSize: '11px', color: 'var(--text-secondary)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                        <span>Hook Strength:</span>
                        <strong style={{ color: 'var(--accent)' }}>{clip.virality_factors.hook_strength}/100</strong>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                        <span>Engagement:</span>
                        <strong style={{ color: 'var(--success)' }}>{clip.virality_factors.engagement_potential}/100</strong>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Pacing:</span>
                        <strong style={{ color: 'var(--accent-hover)' }}>{clip.virality_factors.pacing_score}/100</strong>
                      </div>
                    </div>
                  )}

                  {/* Interactive Text-Based Cue Inspector Button */}
                  <div style={{ marginTop: '6px' }}>
                    <button
                      type="button"
                      className="btn btn-ghost btn-sm"
                      style={{ fontSize: '11px', width: '100%', textAlign: 'center', padding: '4px' }}
                      onClick={() => toggleTranscript(i)}
                    >
                      {expandedTranscript[i] ? '▲ Sembunyikan Text Inspector' : '▼ 📝 Text Inspector & Waveform Seek'}
                    </button>

                    {expandedTranscript[i] && (
                      <div style={{ marginTop: '8px', padding: '8px', background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '6px', fontSize: '12px', maxHeight: '180px', overflowY: 'auto' }}>
                        <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', marginBottom: '6px', textTransform: 'uppercase', fontWeight: 600 }}>
                          Klik kata untuk seek video player:
                        </div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', lineHeight: 1.6 }}>
                          {(clip.metadata?.segments || []).flatMap(s => s.words || []).length > 0 ? (
                            (clip.metadata?.segments || []).flatMap(s => s.words || []).map((w, wIdx) => (
                              <span
                                key={wIdx}
                                onClick={() => seekVideo(i, Math.max(0, w.start - (clip.start_time || 0)))}
                                style={{
                                  cursor: 'pointer',
                                  padding: '1px 4px',
                                  borderRadius: '3px',
                                  background: 'var(--bg-tertiary)',
                                  transition: 'background var(--transition-fast)',
                                }}
                                title={`Jump to ${w.start?.toFixed(1)}s`}
                                onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--accent-dim)' }}
                                onMouseLeave={(e) => { e.currentTarget.style.background = 'var(--bg-tertiary)' }}
                              >
                                {w.word}
                              </span>
                            ))
                          ) : (
                            <span style={{ color: 'var(--text-muted)', fontSize: '11px' }}>
                              {clip.metadata?.description || clip.title || 'Transcript cues not attached.'}
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="clip-actions" style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
                    <a href={clip.download_url} download className="btn btn-secondary btn-sm" style={{ flex: 1, textAlign: 'center' }}>
                      ⬇️ Download MP4
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Activity Log */}
      {job.log && job.log.length > 0 && (
        <div style={{ marginTop: '24px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '10px' }}>📋 Activity Log</h3>
          <div className="log-viewer">
            {job.log.map((line, i) => <div key={i}>{line}</div>)}
          </div>
        </div>
      )}
    </div>
  )
}

export default JobDetail
