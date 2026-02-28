import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, TestTube, ExternalLink } from 'lucide-react'
import Header from '../components/layout/Header'
import Modal from '../components/common/Modal'
import { getTargets, createTarget, deleteTarget, testTarget } from '../api/targets'
import { formatDate, formatLatency } from '../utils/formatters'

export default function Targets() {
  const queryClient = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [testResult, setTestResult] = useState(null)
  const [testingId, setTestingId] = useState(null)
  const [form, setForm] = useState({
    name: '', description: '', api_url: '', api_method: 'POST',
    headers: '{}', request_template: '{"query": "{{input}}"}', response_path: 'response',
  })

  const { data: targets } = useQuery({ queryKey: ['targets'], queryFn: getTargets })

  const createMutation = useMutation({
    mutationFn: (data) => createTarget({ ...data, headers: JSON.parse(data.headers || '{}') }),
    onSuccess: () => { queryClient.invalidateQueries(['targets']); setShowCreate(false); setForm({ name: '', description: '', api_url: '', api_method: 'POST', headers: '{}', request_template: '{"query": "{{input}}"}', response_path: 'response' }) },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteTarget,
    onSuccess: () => queryClient.invalidateQueries(['targets']),
  })

  const handleTest = async (id) => {
    setTestingId(id)
    setTestResult(null)
    try {
      const result = await testTarget(id, { input_text: 'Hello, how are you?' })
      setTestResult({ id, ...result })
    } catch (e) {
      setTestResult({ id, success: false, error: e.message, status_code: 0, latency_ms: 0 })
    }
    setTestingId(null)
  }

  return (
    <div>
      <Header
        title="Targets"
        subtitle="Configure LLM applications to evaluate"
        actions={
          <button onClick={() => setShowCreate(true)} className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
            <Plus size={18} /> Add Target
          </button>
        }
      />

      {targets && targets.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {targets.map(t => (
            <div key={t.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-sm font-semibold text-gray-900">{t.name}</h3>
                  {t.description && <p className="text-xs text-gray-500 mt-0.5">{t.description}</p>}
                </div>
                <button onClick={() => deleteMutation.mutate(t.id)} className="text-gray-400 hover:text-red-500 transition-colors">
                  <Trash2 size={16} />
                </button>
              </div>

              <div className="space-y-2 text-xs text-gray-600 mb-4">
                <div className="flex items-center gap-1.5">
                  <ExternalLink size={12} />
                  <span className="truncate">{t.api_url}</span>
                </div>
                <div><span className="font-medium">Method:</span> {t.api_method}</div>
                <div><span className="font-medium">Response Path:</span> {t.response_path}</div>
                <div className="text-gray-400">{formatDate(t.created_at)}</div>
              </div>

              <button
                onClick={() => handleTest(t.id)}
                disabled={testingId === t.id}
                className="w-full flex items-center justify-center gap-2 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50 transition-colors"
              >
                <TestTube size={14} />
                {testingId === t.id ? 'Testing...' : 'Test Connection'}
              </button>

              {testResult && testResult.id === t.id && (
                <div className={`mt-3 p-3 rounded-lg text-xs ${testResult.success ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'}`}>
                  <p className="font-medium">{testResult.success ? 'Connection OK' : 'Connection Failed'}</p>
                  <p>Status: {testResult.status_code} | Latency: {formatLatency(testResult.latency_ms)}</p>
                  {testResult.error && <p className="mt-1">Error: {testResult.error}</p>}
                  {testResult.response_text && <p className="mt-1 truncate">Response: {testResult.response_text}</p>}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center text-gray-400">
          No targets configured. Add one to start evaluating.
        </div>
      )}

      <Modal isOpen={showCreate} onClose={() => setShowCreate(false)} title="Add Target" size="md">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="My LLM App" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="Production chatbot API" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">API URL</label>
            <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.api_url} onChange={e => setForm({...form, api_url: e.target.value})} placeholder="http://localhost:8000/query" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">HTTP Method</label>
              <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.api_method} onChange={e => setForm({...form, api_method: e.target.value})}>
                <option>POST</option>
                <option>GET</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Response JSON Path</label>
              <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.response_path} onChange={e => setForm({...form, response_path: e.target.value})} />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Headers (JSON)</label>
            <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono" value={form.headers} onChange={e => setForm({...form, headers: e.target.value})} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Request Template (use {"{{input}}"} as placeholder)</label>
            <textarea className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono h-20" value={form.request_template} onChange={e => setForm({...form, request_template: e.target.value})} />
          </div>
          <button onClick={() => createMutation.mutate(form)} disabled={!form.name || !form.api_url} className="w-full py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            Add Target
          </button>
        </div>
      </Modal>
    </div>
  )
}
