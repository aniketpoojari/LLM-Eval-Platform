import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts'
import { Plus } from 'lucide-react'
import Header from '../components/layout/Header'
import DataTable from '../components/common/DataTable'
import Modal from '../components/common/Modal'
import StatusBadge from '../components/common/StatusBadge'
import ProgressBar from '../components/common/ProgressBar'
import { getEvaluations, createEvaluation, getEvalResults } from '../api/evaluations'
import { getTargets } from '../api/targets'
import { formatScore, formatDate, getScoreColor } from '../utils/formatters'
import { DIMENSIONS, CHART_COLORS } from '../utils/constants'

export default function Evaluations() {
  const queryClient = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [selectedEval, setSelectedEval] = useState(null)
  const [form, setForm] = useState({ name: '', target_id: '', dimensions: DIMENSIONS.map(d => d.value), queriesText: '' })

  const { data: evaluations, isLoading } = useQuery({ queryKey: ['evaluations'], queryFn: getEvaluations, refetchInterval: 5000 })
  const { data: targets } = useQuery({ queryKey: ['targets'], queryFn: getTargets })
  const { data: results } = useQuery({
    queryKey: ['evalResults', selectedEval?.id],
    queryFn: () => getEvalResults(selectedEval.id),
    enabled: !!selectedEval,
  })

  const createMutation = useMutation({
    mutationFn: createEvaluation,
    onSuccess: () => { queryClient.invalidateQueries(['evaluations']); setShowCreate(false) },
  })

  const handleCreate = () => {
    const queries = form.queriesText.split('\n').filter(Boolean).map(line => {
      const [input, expected] = line.split('|').map(s => s.trim())
      return { input, expected_output: expected || null }
    })
    createMutation.mutate({ ...form, queries })
  }

  const columns = [
    { key: 'name', label: 'Name' },
    { key: 'status', label: 'Status', render: (v) => <StatusBadge status={v} /> },
    { key: 'total_queries', label: 'Queries', render: (v, row) => `${row.completed_queries}/${v}` },
    { key: 'avg_score', label: 'Avg Score', render: (v) => <span className={getScoreColor(v)}>{formatScore(v)}</span> },
    { key: 'created_at', label: 'Created', render: (v) => formatDate(v) },
  ]

  const radarData = selectedEval && results ? (() => {
    const dimAvgs = {}
    results.forEach(r => {
      Object.entries(r.scores).forEach(([dim, score]) => {
        if (!dimAvgs[dim]) dimAvgs[dim] = []
        dimAvgs[dim].push(score)
      })
    })
    return Object.entries(dimAvgs).map(([dim, scores]) => ({
      dimension: dim.charAt(0).toUpperCase() + dim.slice(1),
      score: scores.reduce((a, b) => a + b, 0) / scores.length,
    }))
  })() : []

  return (
    <div>
      <Header
        title="Evaluations"
        subtitle="Run multi-dimension evaluations against your LLM targets"
        actions={
          <button onClick={() => setShowCreate(true)} className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
            <Plus size={18} /> New Evaluation
          </button>
        }
      />

      {evaluations?.some(e => e.status === 'running') && (
        <div className="mb-6">
          {evaluations.filter(e => e.status === 'running').map(e => (
            <div key={e.id} className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-2">
              <p className="text-sm font-medium text-blue-800 mb-2">{e.name} - Running</p>
              <ProgressBar current={e.completed_queries} total={e.total_queries} color="indigo" />
            </div>
          ))}
        </div>
      )}

      <DataTable columns={columns} data={evaluations} onRowClick={setSelectedEval} emptyMessage="No evaluations yet. Create one to get started." />

      <Modal isOpen={showCreate} onClose={() => setShowCreate(false)} title="New Evaluation" size="md">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="My Evaluation" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target</label>
            <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.target_id} onChange={e => setForm({...form, target_id: e.target.value})}>
              <option value="">Select target...</option>
              {(targets || []).map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Dimensions</label>
            <div className="flex flex-wrap gap-2">
              {DIMENSIONS.map(d => (
                <label key={d.value} className="flex items-center gap-1.5 text-sm">
                  <input type="checkbox" checked={form.dimensions.includes(d.value)} onChange={e => {
                    const dims = e.target.checked ? [...form.dimensions, d.value] : form.dimensions.filter(x => x !== d.value)
                    setForm({...form, dimensions: dims})
                  }} />
                  {d.label}
                </label>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Queries (one per line, optional expected output after |)</label>
            <textarea className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm h-32" value={form.queriesText} onChange={e => setForm({...form, queriesText: e.target.value})} placeholder={"What is AI?\nExplain machine learning | Machine learning is a subset of AI..."} />
          </div>
          <button onClick={handleCreate} disabled={!form.name || !form.target_id || !form.queriesText} className="w-full py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            Start Evaluation
          </button>
        </div>
      </Modal>

      <Modal isOpen={!!selectedEval} onClose={() => setSelectedEval(null)} title={selectedEval?.name || 'Evaluation Details'} size="lg">
        {selectedEval && (
          <div>
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold">{formatScore(selectedEval.avg_score)}</p>
                <p className="text-xs text-gray-500">Avg Score</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold">{selectedEval.completed_queries}/{selectedEval.total_queries}</p>
                <p className="text-xs text-gray-500">Queries</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <StatusBadge status={selectedEval.status} />
              </div>
            </div>

            {radarData.length > 0 && (
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-gray-700 mb-3">Score by Dimension</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 12 }} />
                    <PolarRadiusAxis domain={[0, 5]} tick={{ fontSize: 10 }} />
                    <Radar dataKey="score" stroke={CHART_COLORS[0]} fill={CHART_COLORS[0]} fillOpacity={0.3} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            )}

            {results && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-3">Individual Results</h4>
                <div className="space-y-2 max-h-64 overflow-auto">
                  {results.map((r, i) => (
                    <div key={r.id} className="border border-gray-200 rounded-lg p-3">
                      <p className="text-sm font-medium text-gray-900 mb-1">Q: {r.input_text}</p>
                      <p className="text-xs text-gray-500 mb-2 line-clamp-2">A: {r.actual_output}</p>
                      <div className="flex gap-3 text-xs">
                        {Object.entries(r.scores).map(([dim, score]) => (
                          <span key={dim} className={getScoreColor(score)}>{dim}: {score}/5</span>
                        ))}
                        <span className="text-gray-400">Avg: {formatScore(r.avg_score)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}
