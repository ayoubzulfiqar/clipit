const API_BASE = '/api'

export function getApiKey() {
  return localStorage.getItem('clipit_api_key') || ''
}

export function setApiKey(key) {
  if (key) {
    localStorage.setItem('clipit_api_key', key.trim())
  } else {
    localStorage.removeItem('clipit_api_key')
  }
}

function authHeaders(headers = {}) {
  const key = getApiKey()
  const res = { ...headers }
  if (key) {
    res['X-API-Key'] = key
  }
  return res
}

export async function fetchJobs(params = {}) {
  const query = new URLSearchParams()
  if (params.search) query.append('search', params.search)
  if (params.tag) query.append('tag', params.tag)
  if (params.status) query.append('status', params.status)
  if (params.page) query.append('page', params.page)
  if (params.limit) query.append('limit', params.limit)

  const url = `${API_BASE}/jobs${query.toString() ? `?${query.toString()}` : ''}`
  const res = await fetch(url, { headers: authHeaders() })
  if (!res.ok) throw new Error('Failed to fetch jobs')
  return res.json()
}

export async function fetchJob(jobId) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`, { headers: authHeaders() })
  if (!res.ok) throw new Error('Job not found')
  return res.json()
}

export async function createJob(payload) {
  const res = await fetch(`${API_BASE}/jobs`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to create job')
  }
  return res.json()
}

export async function cancelJob(jobId) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/cancel`, {
    method: 'POST',
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error('Failed to cancel job')
  return res.json()
}

export async function retryJob(jobId) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/retry`, {
    method: 'POST',
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error('Failed to retry job')
  return res.json()
}

export async function cloneJob(jobId) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/clone`, {
    method: 'POST',
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error('Failed to clone job')
  return res.json()
}

export async function updateJobTags(jobId, tags) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/tags`, {
    method: 'PATCH',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ tags }),
  })
  if (!res.ok) throw new Error('Failed to update job tags')
  return res.json()
}

export async function bulkJobsAction(action, jobIds, tags = []) {
  const res = await fetch(`${API_BASE}/jobs/bulk`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ action, job_ids: jobIds, tags }),
  })
  if (!res.ok) throw new Error(`Bulk action '${action}' failed`)
  return res.json()
}

export async function deleteJob(jobId) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`, {
    method: 'DELETE',
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error('Failed to delete job')
  return res.json()
}

export async function fetchPresets() {
  const res = await fetch(`${API_BASE}/presets`, { headers: authHeaders() })
  if (!res.ok) throw new Error('Failed to fetch presets')
  return res.json()
}

export async function createPreset(payload) {
  const res = await fetch(`${API_BASE}/presets`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error('Failed to create preset')
  return res.json()
}

export async function deletePreset(presetId) {
  const res = await fetch(`${API_BASE}/presets/${presetId}`, {
    method: 'DELETE',
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error('Failed to delete preset')
  return res.json()
}

export function getZipDownloadUrl(jobId) {
  return `${API_BASE}/outputs/${jobId}/zip`
}

export async function uploadVideo(file, onProgress) {
  const formData = new FormData()
  formData.append('file', file)

  const res = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    headers: authHeaders(),
    body: formData,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Upload failed')
  }
  return res.json()
}

export async function fetchSettings() {
  const res = await fetch(`${API_BASE}/settings`, { headers: authHeaders() })
  if (!res.ok) throw new Error('Failed to fetch settings')
  return res.json()
}

export async function updateSettings(payload) {
  const res = await fetch(`${API_BASE}/settings`, {
    method: 'PUT',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error('Failed to update settings')
  return res.json()
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`)
  if (!res.ok) throw new Error('Health check failed')
  return res.json()
}

export async function fetchReadiness() {
  const res = await fetch(`${API_BASE}/health/ready`)
  if (!res.ok) throw new Error('Readiness check failed')
  return res.json()
}

export function createSSEConnection(jobId, onMessage) {
  const eventSource = new EventSource(`${API_BASE}/jobs/${jobId}/status`)

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onMessage(data)
    } catch (e) {
      console.error('SSE parse error:', e)
    }
  }

  eventSource.onerror = () => {
    eventSource.close()
  }

  return eventSource
}
