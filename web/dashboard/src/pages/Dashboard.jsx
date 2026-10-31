import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { fetchJobs, fetchHealth, bulkJobsAction, getZipDownloadUrl } from '../api'

const STATUS_LABELS = {
  queued: 'Queued',
  downloading: 'Downloading',
  transcribing: 'Transcribing',
  analyzing: 'Analyzing',
  rendering: 'Rendering',
  completed: 'Completed',
  failed: 'Failed',
  cancelled: 'Cancelled',
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleString('id-ID', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function Dashboard() {
  const [jobs, setJobs] = useState([])
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [selectedIds, setSelectedIds] = useState([])
  const [bulkBusy, setBulkBusy] = useState(false)

  const loadData = async () => {
    try {
      const [jobsData, healthData] = await Promise.all([
        fetchJobs({ search, status: statusFilter === 'all' ? undefined : statusFilter }),
        fetchHealth(),
      ])
      setJobs(jobsData.jobs || [])
      setHealth(healthData)
    } catch (err) {
      console.error('Failed to load dashboard:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 5000)
    return () => clearInterval(interval)
  }, [search, statusFilter])

  const totalCompleted = jobs.filter(j => j.status === 'completed').length
  const totalClips = jobs.reduce((acc, j) => acc + (j.clips?.length || 0), 0)

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedIds(jobs.map(j => j.id))
    } else {
      setSelectedIds([])
    }
  }

  const handleSelectOne = (id) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    )
  }

  const handleBulkAction = async (action) => {
    if (!selectedIds.length || bulkBusy) return
    if (action === 'delete' && !confirm(`Yakin ingin menghapus ${selectedIds.length} job terpilih?`)) {
      return
    }

    setBulkBusy(true)
    try {
      await bulkJobsAction(action, selectedIds)
      setSelectedIds([])
      await loadData()
    } catch (err) {
      alert(`Bulk action failed: ${err.message}`)
    } finally {
      setBulkBusy(false)
    }
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h2>Dashboard</h2>
          <p>Overview semua clipping jobs dan status render</p>
        </div>
        <Link to="/new" className="btn btn-primary">
          ➕ New Job
        </Link>
      </div>

      {/* Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', marginBottom: '24px' }}>
        <div className="card">
          <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.05em' }}>Total Jobs</div>
          <div style={{ fontSize: '28px', fontWeight: 800, marginTop: '4px', background: 'linear-gradient(135deg, var(--accent), #c4b5fd)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>{jobs.length}</div>
        </div>
        <div className="card">
          <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.05em' }}>Completed</div>
          <div style={{ fontSize: '28px', fontWeight: 800, marginTop: '4px', color: 'var(--success)' }}>{totalCompleted}</div>
        </div>
        <div className="card">
          <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.05em' }}>Total Clips</div>
          <div style={{ fontSize: '28px', fontWeight: 800, marginTop: '4px', color: 'var(--accent-hover)' }}>{totalClips}</div>
        </div>
        <div className="card">
          <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.05em' }}>System</div>
          <div style={{ fontSize: '12px', marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <span style={{ color: health?.gpu_available ? 'var(--success)' : 'var(--text-tertiary)' }}>
              {health?.gpu_available ? '✅ GPU Active' : '⚪ CPU Mode'}
            </span>
            <span style={{ color: health?.ffmpeg_available ? 'var(--success)' : 'var(--error)' }}>
              {health?.ffmpeg_available ? '✅ FFmpeg Ready' : '❌ FFmpeg Missing'}
            </span>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="card" style={{ marginBottom: '16px', display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', gap: '8px', flex: 1, minWidth: '240px' }}>
          <input
            type="text"
            className="form-input"
            placeholder="🔍 Cari job ID, URL, nama file, atau tag..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', gap: '6px' }}>
          {['all', 'completed', 'rendering', 'failed'].map((st) => (
            <button
              key={st}
              type="button"
              className={`btn btn-sm ${statusFilter === st ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setStatusFilter(st)}
            >
              {st === 'all' ? 'Semua' : st.charAt(0).toUpperCase() + st.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Bulk Action Bar */}
      {selectedIds.length > 0 && (
        <div className="card" style={{ marginBottom: '16px', background: 'rgba(99, 102, 241, 0.1)', borderColor: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
          <span style={{ fontSize: '13px', fontWeight: 600 }}>
            📌 {selectedIds.length} job terpilih
          </span>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              disabled={bulkBusy}
              onClick={() => handleBulkAction('retry')}
            >
              🔄 Retry
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              disabled={bulkBusy}
              onClick={() => handleBulkAction('cancel')}
            >
              ⏹ Cancel
            </button>
            <button
              type="button"
              className="btn btn-danger btn-sm"
              disabled={bulkBusy}
              onClick={() => handleBulkAction('delete')}
            >
              🗑 Delete
            </button>
          </div>
        </div>
      )}

      {/* Select All Checkbox */}
      {jobs.length > 0 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', fontSize: '12px', color: 'var(--text-secondary)' }}>
          <input
            type="checkbox"
            id="select-all"
            checked={selectedIds.length === jobs.length && jobs.length > 0}
            onChange={handleSelectAll}
          />
          <label htmlFor="select-all" style={{ cursor: 'pointer' }}>Select All ({jobs.length} jobs)</label>
        </div>
      )}

      {/* Job List */}
      {loading ? (
        <div className="empty-state">
          <div className="spinner"></div>
          <p style={{ marginTop: '12px' }}>Loading...</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="empty-state">
          <div className="icon">🎬</div>
          <h3>Belum ada job</h3>
          <p>Buat job pertama untuk memulai clipping video otomatis dengan AI.</p>
          <Link to="/new" className="btn btn-primary">➕ Create First Job</Link>
        </div>
      ) : (
        <div className="job-grid">
          {jobs.map(job => (
            <div key={job.id} className="job-card" style={{ position: 'relative' }}>
              <div style={{ position: 'absolute', top: '16px', right: '16px', zIndex: 2, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input
                  type="checkbox"
                  checked={selectedIds.includes(job.id)}
                  onChange={() => handleSelectOne(job.id)}
                  onClick={(e) => e.stopPropagation()}
                />
              </div>

              <Link to={`/job/${job.id}`} style={{ textDecoration: 'none', color: 'inherit', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', width: '100%' }}>
                <div className="job-info" style={{ paddingRight: '40px' }}>
                  <h3>
                    {job.url ? new URL(job.url).hostname.replace('www.', '') : job.upload_filename || 'Upload'}
                    <span style={{ color: 'var(--text-muted)', fontWeight: 400, marginLeft: '8px', fontSize: '12px' }}>#{job.id}</span>
                  </h3>
                  <div className="job-meta">
                    <span>{formatDate(job.created_at)}</span>
                    {job.clips?.length > 0 && <span>🎞️ {job.clips.length} clips</span>}
                    {job.progress?.message && !['completed', 'failed'].includes(job.status) && (
                      <span style={{ color: 'var(--accent-hover)' }}>{job.progress.message}</span>
                    )}
                    {job.error && <span style={{ color: 'var(--error)' }}>⚠ Error</span>}
                  </div>

                  {/* Tags */}
                  {job.tags && job.tags.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '8px' }}>
                      {job.tags.map((t, idx) => (
                        <span key={idx} style={{ fontSize: '11px', background: 'var(--bg-tertiary)', padding: '2px 6px', borderRadius: '4px', color: 'var(--text-secondary)' }}>
                          #{t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
                  <span className={`badge badge-${job.status}`}>
                    {STATUS_LABELS[job.status] || job.status}
                  </span>
                  {job.status === 'completed' && (
                    <a
                      href={getZipDownloadUrl(job.id)}
                      download={`clipit_${job.id}.zip`}
                      className="btn btn-secondary btn-sm"
                      style={{ fontSize: '11px', padding: '4px 8px' }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      📦 ZIP
                    </a>
                  )}
                </div>
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Dashboard
