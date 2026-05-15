import { useState, useEffect, useCallback } from 'react'

const API = ''

async function apiFetch(path, opts = {}) {
  const res = await fetch(API + path, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  if (res.status === 204) return null
  return res.json()
}

function Badge({ type, value }) {
  return <span className={`badge badge-${value}`}>{value.replace('_', ' ')}</span>
}

function TaskCheck({ done, onToggle }) {
  return (
    <button className={`task-check ${done ? 'checked' : ''}`} onClick={onToggle} title={done ? 'Mark open' : 'Mark done'}>
      {done && (
        <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2.5">
          <polyline points="2,6 5,9 10,3" />
        </svg>
      )}
    </button>
  )
}

function DetailPanel({ caseData, onTaskToggle }) {
  const openCount = caseData.tasks.filter(t => t.status === 'open').length
  return (
    <div className="detail-panel">
      <h2>{caseData.title}</h2>
      <p className="detail-about">{caseData.about}</p>
      <div className="detail-meta">
        <Badge value={caseData.status} />
        <Badge value={caseData.priority} />
      </div>

      <div className="tasks-title">
        Tasks — {openCount} open of {caseData.tasks.length}
      </div>

      {caseData.tasks.map(task => (
        <div key={task.id} className={`task-item ${task.status === 'closed' ? 'done' : ''}`}>
          <TaskCheck
            done={task.status === 'closed'}
            onToggle={() => onTaskToggle(caseData.id, task.id, task.status)}
          />
          <span className="task-label">{task.title}</span>
          <Badge value={task.status} />
        </div>
      ))}
    </div>
  )
}

function CaseCard({ caseData, active, onClick }) {
  const openTasks = caseData.tasks.filter(t => t.status === 'open').length
  return (
    <div className={`case-card ${active ? 'active' : ''}`} onClick={onClick}>
      <div className="card-header">
        <span className="card-title">{caseData.title}</span>
        <Badge value={caseData.status} />
      </div>
      <p className="card-about">{caseData.about}</p>
      <div className="card-footer">
        <Badge value={caseData.priority} />
        <span className="task-count">{openTasks} task{openTasks !== 1 ? 's' : ''} open</span>
      </div>
    </div>
  )
}

function NewCaseModal({ onClose, onCreate }) {
  const [form, setForm] = useState({ title: '', about: '', priority: 'medium' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const set = (field) => (e) => setForm(f => ({ ...f, [field]: e.target.value }))

  async function submit(e) {
    e.preventDefault()
    if (!form.title.trim() || !form.about.trim()) {
      setError('Title and description are required.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const created = await apiFetch('/cases/', { method: 'POST', body: JSON.stringify(form) })
      onCreate(created)
      onClose()
    } catch (err) {
      setError('Failed to create case. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <h2>New Case</h2>
        {error && <div className="error-banner">{error}</div>}
        <form onSubmit={submit}>
          <div className="form-group">
            <label>Case Title</label>
            <input
              type="text"
              placeholder="e.g. Fraud Investigation – John Smith"
              value={form.title}
              onChange={set('title')}
              autoFocus
            />
          </div>
          <div className="form-group">
            <label>What is this case about?</label>
            <textarea
              placeholder="Describe the issue, context, or reason for opening this case..."
              value={form.about}
              onChange={set('about')}
            />
          </div>
          <div className="form-group">
            <label>Priority</label>
            <select value={form.priority} onChange={set('priority')}>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
          <div className="modal-actions">
            <button type="button" className="btn btn-ghost" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating…' : 'Create Case'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function App() {
  const [cases, setCases] = useState([])
  const [selected, setSelected] = useState(null)
  const [showModal, setShowModal] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    try {
      const data = await apiFetch('/cases/')
      setCases(data)
    } catch {
      setError('Could not load cases.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  function handleCreate(newCase) {
    setCases(prev => [newCase, ...prev])
    setSelected(newCase)
  }

  async function handleTaskToggle(caseId, taskId, currentStatus) {
    const newStatus = currentStatus === 'open' ? 'closed' : 'open'
    try {
      const updated = await apiFetch(`/cases/${caseId}/tasks/${taskId}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: newStatus }),
      })
      setCases(prev => prev.map(c =>
        c.id !== caseId ? c : {
          ...c,
          tasks: c.tasks.map(t => t.id === taskId ? updated : t)
        }
      ))
      if (selected?.id === caseId) {
        setSelected(prev => ({
          ...prev,
          tasks: prev.tasks.map(t => t.id === taskId ? updated : t)
        }))
      }
    } catch {
      setError('Failed to update task.')
    }
  }

  function selectCase(c) {
    setSelected(prev => prev?.id === c.id ? null : c)
  }

  const selectedFresh = cases.find(c => c.id === selected?.id) ?? selected

  return (
    <>
      <header className="header">
        <h1><span>◈</span> Case Management</h1>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          + New Case
        </button>
      </header>

      <main className="main">
        <div className="page-title">
          Cases
          <small>{cases.length} total</small>
        </div>

        {error && <div className="error-banner">{error}</div>}

        {loading ? (
          <div className="loading">Loading cases…</div>
        ) : (
          <div className="cases-grid">
            {cases.length === 0 ? (
              <div className="empty-state">
                <h3>No cases yet</h3>
                <p>Click <strong>New Case</strong> to open your first case.</p>
              </div>
            ) : (
              cases.map(c => (
                <CaseCard
                  key={c.id}
                  caseData={c}
                  active={selected?.id === c.id}
                  onClick={() => selectCase(c)}
                />
              ))
            )}
          </div>
        )}

        {selectedFresh && (
          <DetailPanel
            caseData={selectedFresh}
            onTaskToggle={handleTaskToggle}
          />
        )}
      </main>

      {showModal && (
        <NewCaseModal
          onClose={() => setShowModal(false)}
          onCreate={handleCreate}
        />
      )}
    </>
  )
}
