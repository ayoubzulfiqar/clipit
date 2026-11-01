import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  createBatchJobs,
  fetchBatchStatus,
  cancelBatchJobs,
  fetchPresets,
} from '../api'
import { showToast } from '../components/Toast'

export default function BatchStudio() {
  const [urlsText, setUrlsText] = useState('')
  const [presets, setPresets] = useState([])
  const [selectedPreset, setSelectedPreset] = useState('')
  const [ratio, setRatio] = useState('9:16')
  const [clipCount, setClipCount] = useState(3)
  const [webhookUrl, setWebhookUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [activeBatchId, setActiveBatchId] = useState(() => localStorage.getItem('clipit_active_batch') || null)
  const [batchStatus, setBatchStatus] = useState(null)
  const [polling, setPolling] = useState(false)

  useEffect(() => {
    fetchPresets()
      .then((data) => setPresets(data || []))
      .catch((err) => console.error('Failed to load presets:', err))
  }, [])

  useEffect(() => {
    if (!activeBatchId) return
    let interval = null

    const poll = async () => {
      try {
        const data = await fetchBatchStatus(activeBatchId)
        setBatchStatus(data)
        if (data.completed + data.failed >= data.total && data.total > 0) {
          setPolling(false)
          clearInterval(interval)
          showToast(`Batch ${activeBatchId} finished processing!`, 'success')
        }
      } catch (err) {
        console.error('Failed to poll batch status:', err)
      }
    }

    poll()
    interval = setInterval(poll, 3000)
    setPolling(true)

    return () => clearInterval(interval)
  }, [activeBatchId])

  const handleSubmit = async (e) => {
    e.preventDefault()
    const urls = urlsText
      .split('\n')
      .map((u) => u.trim())
      .filter((u) => u.length > 0)

    if (urls.length === 0) {
      showToast('Please enter at least one video URL', 'error')
      return
    }

    setLoading(true)
    try {
      const items = urls.map((url) => ({
        url,
        pilihan_rasio: ratio,
        jumlah_klip: parseInt(clipCount, 10),
        preset: selectedPreset || undefined,
      }))

      const payload = {
        items,
        default_config: {
          pilihan_rasio: ratio,
          jumlah_klip: parseInt(clipCount, 10),
          preset: selectedPreset || undefined,
        },
        batch_webhook_url: webhookUrl.trim() || undefined,
      }

      const res = await createBatchJobs(payload)
      setActiveBatchId(res.batch_id)
      localStorage.setItem('clipit_active_batch', res.batch_id)
      setUrlsText('')
      showToast(`Batch ${res.batch_id} submitted with ${res.total_jobs} jobs!`, 'success')
    } catch (err) {
      showToast(err.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleCancelBatch = async () => {
    if (!activeBatchId) return
    if (!window.confirm('Cancel all pending and running jobs in this batch?')) return
    try {
      await cancelBatchJobs(activeBatchId)
      showToast(`Batch ${activeBatchId} cancelled`, 'info')
      const updated = await fetchBatchStatus(activeBatchId)
      setBatchStatus(updated)
    } catch (err) {
      showToast(err.message, 'error')
    }
  }

  const percentComplete = batchStatus
    ? Math.round(((batchStatus.completed + batchStatus.failed) / (batchStatus.total || 1)) * 100)
    : 0

  return (
    <div style={{ padding: '24px 32px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2 style={{ fontSize: '24px', fontWeight: 800, margin: 0 }}>📦 Batch Studio</h2>
          <p style={{ color: 'var(--text-muted)', margin: '4px 0 0', fontSize: '14px' }}>
            Submit multiple URLs for high-throughput parallel AI clipping.
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '24px' }}>
        {/* Form Card */}
        <div className="card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '17px', fontWeight: 700, marginTop: 0, marginBottom: '16px' }}>
            Submit New Batch
          </h3>

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                Video URLs (One per line)
              </label>
              <textarea
                rows={6}
                value={urlsText}
                onChange={(e) => setUrlsText(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=VIDEO_1&#10;https://www.youtube.com/watch?v=VIDEO_2&#10;https://www.youtube.com/watch?v=VIDEO_3"
                className="input-field"
                style={{ width: '100%', fontFamily: 'monospace', fontSize: '13px', resize: 'vertical' }}
              />
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                Supports YouTube videos, playlists, or direct MP4 streams.
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                  Pipeline Preset
                </label>
                <select
                  value={selectedPreset}
                  onChange={(e) => setSelectedPreset(e.target.value)}
                  className="input-field"
                  style={{ width: '100%' }}
                >
                  <option value="">Default (Auto)</option>
                  {presets.map((p) => (
                    <option key={p.name} value={p.name}>
                      {p.name.replace(/_/g, ' ').toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                  Target Ratio
                </label>
                <select
                  value={ratio}
                  onChange={(e) => setRatio(e.target.value)}
                  className="input-field"
                  style={{ width: '100%' }}
                >
                  <option value="9:16">9:16 Portrait (TikTok/Shorts)</option>
                  <option value="1:1">1:1 Square (Feed/LinkedIn)</option>
                  <option value="16:9">16:9 Landscape</option>
                </select>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                  Clips Per Video
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={clipCount}
                  onChange={(e) => setClipCount(e.target.value)}
                  className="input-field"
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                  Batch Webhook (Optional)
                </label>
                <input
                  type="url"
                  placeholder="https://api.yourdomain.com/webhook"
                  value={webhookUrl}
                  onChange={(e) => setWebhookUrl(e.target.value)}
                  className="input-field"
                  style={{ width: '100%' }}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{ width: '100%', padding: '12px', fontSize: '15px', fontWeight: 700 }}
            >
              {loading ? 'Submitting Batch...' : '🚀 Launch Batch Ingestion'}
            </button>
          </form>
        </div>

        {/* Progress & Status Card */}
        <div className="card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '17px', fontWeight: 700, margin: 0 }}>
              Active Batch Monitor
            </h3>
            {activeBatchId && (
              <button
                type="button"
                onClick={handleCancelBatch}
                className="btn btn-ghost btn-sm"
                style={{ color: 'var(--danger)', fontSize: '12px' }}
              >
                Cancel Batch
              </button>
            )}
          </div>

          {!activeBatchId ? (
            <div style={{ textAlign: 'center', padding: '48px 0', color: 'var(--text-muted)' }}>
              <div style={{ fontSize: '32px', marginBottom: '8px' }}>📦</div>
              <p style={{ margin: 0, fontSize: '14px' }}>No active batch running.</p>
              <p style={{ fontSize: '12px', margin: '4px 0 0' }}>Submit a batch on the left to monitor progress here.</p>
            </div>
          ) : !batchStatus ? (
            <div style={{ textAlign: 'center', padding: '36px 0', color: 'var(--text-muted)' }}>
              Loading batch telemetry ({activeBatchId})...
            </div>
          ) : (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '13px' }}>
                <span style={{ fontWeight: 600 }}>Batch ID: {batchStatus.batch_id}</span>
                <span style={{ color: 'var(--accent)', fontWeight: 700 }}>{percentComplete}%</span>
              </div>

              {/* Progress Bar */}
              <div style={{ height: '8px', background: 'var(--border-color)', borderRadius: '4px', overflow: 'hidden', marginBottom: '20px' }}>
                <div
                  style={{
                    height: '100%',
                    width: `${percentComplete}%`,
                    background: 'var(--accent)',
                    transition: 'width 0.3s ease',
                  }}
                />
              </div>

              {/* Counters Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', marginBottom: '20px', textAlign: 'center' }}>
                <div style={{ padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.03)' }}>
                  <div style={{ fontSize: '18px', fontWeight: 800 }}>{batchStatus.total}</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Total</div>
                </div>
                <div style={{ padding: '10px', borderRadius: '8px', background: 'rgba(59, 130, 246, 0.08)' }}>
                  <div style={{ fontSize: '18px', fontWeight: 800, color: '#3b82f6' }}>{batchStatus.processing}</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Processing</div>
                </div>
                <div style={{ padding: '10px', borderRadius: '8px', background: 'rgba(16, 185, 129, 0.08)' }}>
                  <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--success)' }}>{batchStatus.completed}</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Completed</div>
                </div>
                <div style={{ padding: '10px', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.08)' }}>
                  <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--danger)' }}>{batchStatus.failed}</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Failed</div>
                </div>
              </div>

              {/* Jobs List */}
              <h4 style={{ fontSize: '13px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '10px', letterSpacing: '0.5px' }}>
                Jobs in this batch
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '240px', overflowY: 'auto' }}>
                {batchStatus.jobs.map((j) => (
                  <div
                    key={j.job_id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '10px 12px',
                      borderRadius: '8px',
                      background: 'rgba(255,255,255,0.02)',
                      border: '1px solid var(--border-color)',
                      fontSize: '13px',
                    }}
                  >
                    <div style={{ minWidth: 0, flex: 1, marginRight: '10px' }}>
                      <Link
                        to={`/job/${j.job_id}`}
                        style={{ color: 'var(--accent)', fontWeight: 600, textDecoration: 'none', display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
                      >
                        {j.url || j.job_id}
                      </Link>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                        {j.step || j.status} • {j.clips_count || 0} clips
                      </div>
                    </div>
                    <span
                      style={{
                        fontSize: '11px',
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontWeight: 600,
                        textTransform: 'uppercase',
                        background:
                          j.status === 'completed' || j.status === 'done'
                            ? 'rgba(16, 185, 129, 0.15)'
                            : j.status === 'failed' || j.status === 'error'
                            ? 'rgba(239, 68, 68, 0.15)'
                            : 'rgba(59, 130, 246, 0.15)',
                        color:
                          j.status === 'completed' || j.status === 'done'
                            ? 'var(--success)'
                            : j.status === 'failed' || j.status === 'error'
                            ? 'var(--danger)'
                            : '#3b82f6',
                      }}
                    >
                      {j.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
