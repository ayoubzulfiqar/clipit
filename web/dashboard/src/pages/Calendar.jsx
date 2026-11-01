import { useState, useEffect } from 'react'
import { fetchJobs, generateCalendar } from '../api'
import { showToast } from '../components/Toast'

export default function Calendar() {
  const [jobs, setJobs] = useState([])
  const [selectedJobId, setSelectedJobId] = useState('')
  const [platforms, setPlatforms] = useState(['tiktok', 'shorts', 'reels'])
  const [clipsPerDay, setClipsPerDay] = useState(2)
  const [loading, setLoading] = useState(false)
  const [schedule, setSchedule] = useState([])

  useEffect(() => {
    fetchJobs({ status: 'completed', limit: 20 })
      .then((data) => {
        const completed = (data.jobs || data || []).filter(
          (j) => j.status === 'completed' || j.status === 'done' || (j.clips && j.clips.length > 0)
        )
        setJobs(completed)
        if (completed.length > 0) {
          setSelectedJobId(completed[0].id)
        }
      })
      .catch((err) => console.error('Failed to load completed jobs:', err))
  }, [])

  const handleGenerate = async (e) => {
    if (e) e.preventDefault()
    setLoading(true)
    try {
      const res = await generateCalendar({
        job_id: selectedJobId || undefined,
        platforms,
        clips_per_day: parseInt(clipsPerDay, 10),
      })
      setSchedule(res.schedule || [])
      showToast(`Generated ${res.total_slots} optimized publication slots!`, 'success')
    } catch (err) {
      showToast(err.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const togglePlatform = (p) => {
    if (platforms.includes(p)) {
      if (platforms.length === 1) {
        showToast('At least one platform must be selected', 'info')
        return
      }
      setPlatforms(platforms.filter((x) => x !== p))
    } else {
      setPlatforms([...platforms, p])
    }
  }

  const copySlotText = (slot) => {
    const text = `${slot.title}\n\n${slot.caption || ''}\n\n${(slot.hashtags || []).join(' ')}`
    navigator.clipboard.writeText(text)
    showToast(`Copied text for ${slot.platform.toUpperCase()}!`, 'success')
  }

  const exportCSV = () => {
    if (schedule.length === 0) return
    const headers = ['Platform', 'Scheduled Time (UTC)', 'Clip Rank', 'Title', 'Hashtags']
    const rows = schedule.map((s) => [
      s.platform,
      s.scheduled_time_utc || s.scheduled_time,
      s.clip_rank,
      `"${(s.title || '').replace(/"/g, '""')}"`,
      `"${(s.hashtags || []).join(' ')}"`,
    ])
    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `clipit_calendar_${Date.now()}.csv`
    a.click()
    showToast('Exported calendar to CSV!', 'success')
  }

  return (
    <div style={{ padding: '24px 32px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '24px', fontWeight: 800, margin: 0 }}>📅 Social Release Calendar</h2>
          <p style={{ color: 'var(--text-muted)', margin: '4px 0 0', fontSize: '14px' }}>
            Multi-platform publication schedule with algorithmic peak-time engagement slots.
          </p>
        </div>

        {schedule.length > 0 && (
          <button
            type="button"
            onClick={exportCSV}
            className="btn btn-secondary"
            style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
          >
            📊 Export CSV Schedule
          </button>
        )}
      </div>

      {/* Configuration Card */}
      <div className="card" style={{ padding: '20px', marginBottom: '24px' }}>
        <form onSubmit={handleGenerate} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', alignItems: 'end' }}>
          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
              Select Source Job
            </label>
            <select
              value={selectedJobId}
              onChange={(e) => setSelectedJobId(e.target.value)}
              className="input-field"
              style={{ width: '100%' }}
            >
              {jobs.length === 0 ? (
                <option value="">No completed jobs found</option>
              ) : (
                jobs.map((j) => (
                  <option key={j.id} value={j.id}>
                    {j.id} — {j.url ? j.url.slice(0, 32) + '...' : 'Upload'} ({j.clips?.length || 0} clips)
                  </option>
                ))
              )}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
              Target Platforms
            </label>
            <div style={{ display: 'flex', gap: '8px' }}>
              {['tiktok', 'shorts', 'reels', 'linkedin'].map((p) => {
                const active = platforms.includes(p)
                return (
                  <button
                    key={p}
                    type="button"
                    onClick={() => togglePlatform(p)}
                    className={`btn btn-sm ${active ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ textTransform: 'capitalize', fontSize: '12px' }}
                  >
                    {p}
                  </button>
                )
              })}
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
              Cadence (Clips / Day)
            </label>
            <input
              type="number"
              min="1"
              max="5"
              value={clipsPerDay}
              onChange={(e) => setClipsPerDay(e.target.value)}
              className="input-field"
              style={{ width: '100%' }}
            />
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{ width: '100%', padding: '10px', fontWeight: 700 }}
            >
              {loading ? 'Optimizing Schedule...' : '⚡ Generate Calendar'}
            </button>
          </div>
        </form>
      </div>

      {/* Schedule Grid */}
      {schedule.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: '36px', marginBottom: '12px' }}>🗓️</div>
          <p style={{ margin: 0, fontSize: '15px', fontWeight: 600 }}>No Schedule Generated Yet</p>
          <p style={{ margin: '4px 0 0', fontSize: '13px' }}>
            Select a completed job above and click "Generate Calendar" to calculate optimal engagement time slots.
          </p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '16px' }}>
          {schedule.map((slot, index) => {
            const platformColors = {
              tiktok: '#00f2fe',
              shorts: '#ff0000',
              reels: '#e1306c',
              linkedin: '#0a66c2',
            }

            const pColor = platformColors[slot.platform.toLowerCase()] || 'var(--accent)'

            return (
              <div
                key={index}
                className="card"
                style={{
                  padding: '18px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  borderTop: `3px solid ${pColor}`,
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <span
                      style={{
                        fontSize: '11px',
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        padding: '2px 8px',
                        borderRadius: '4px',
                        background: 'rgba(255,255,255,0.06)',
                        color: pColor,
                      }}
                    >
                      {slot.platform}
                    </span>
                    <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600 }}>
                      🕒 {slot.scheduled_time_utc ? new Date(slot.scheduled_time_utc).toLocaleString() : slot.scheduled_time}
                    </span>
                  </div>

                  <h4 style={{ fontSize: '15px', fontWeight: 700, margin: '0 0 8px', lineHeight: '1.4' }}>
                    {slot.title || `Clip Rank #${slot.clip_rank}`}
                  </h4>

                  {slot.caption && (
                    <p style={{ fontSize: '12px', color: 'var(--text-muted)', margin: '0 0 10px', lineHeight: '1.4' }}>
                      {slot.caption}
                    </p>
                  )}

                  {slot.hashtags && slot.hashtags.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '14px' }}>
                      {slot.hashtags.slice(0, 4).map((tag, tIdx) => (
                        <span key={tIdx} style={{ fontSize: '10px', color: 'var(--accent)', background: 'rgba(99,102,241,0.1)', padding: '1px 6px', borderRadius: '4px' }}>
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border-color)', paddingTop: '12px' }}>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    Clip #{slot.clip_rank}
                  </span>
                  <button
                    type="button"
                    onClick={() => copySlotText(slot)}
                    className="btn btn-secondary btn-sm"
                    style={{ fontSize: '11px', padding: '4px 8px' }}
                  >
                    📋 Copy Text
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
