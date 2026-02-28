import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { Plus } from 'lucide-react'
import Header from '../components/layout/Header'
import DataTable from '../components/common/DataTable'
import Modal from '../components/common/Modal'
import StatusBadge from '../components/common/StatusBadge'
import { getABTests, createABTest, getABStats } from '../api/abTests'
import { getTargets } from '../api/targets'
import { formatScore, formatDate } from '../utils/formatters'
import { DIMENSIONS, CHART_COLORS } from '../utils/constants'

export default function ABTests() {
  const queryClient = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [selectedTest, setSelectedTest] = useState(null)
  const [form, setForm] = useState({ name: '', target_a_id: '', target_b_id: '', dimensions: ['factuality', 'relevance', 'coherence'], queriesText: '' })

  const { data: tests } = useQuery({ queryKey: ['abTests'], queryFn: getABTests, refetchInterval: 5000 })
  const { data: targets } = useQuery({ queryKey: ['targets'], queryFn: getTargets })
  const { data: stats } = useQuery({
    queryKey: ['abStats', selectedTest?.id],
    queryFn: () => getABStats(selectedTest.id),
    enabled: !!selectedTest && selectedTest.status === 'completed',
  })

  const createMutation = useMutation({
    mutationFn: createABTest,
    onSuccess: () => { queryClient.invalidateQueries(['abTests']); setShowCreate(false) },
  })

  const handleCreate = () => {
    const queries = form.queriesText.split('\n').filter(Boolean)
    createMutation.mutate({ ...form, queries })
  }

  const columns = [
    { key: 'name', label: 'Experiment' },
    { key: 'status', label: 'Status', render: (v) => <StatusBadge status={v} /> },
    { key: 'total_queries', label: 'Queries', render: (v, row) => `${row.completed_queries}/${v}` },
    { key: 'winner', label: 'Winner', render: (v) => v ? <span className="font-semibold text-green-600">Target {v}</span> : '-' },
    { key: 'statistical_significance', label: 'p-value', render: (v) => v !== null ? v.toFixed(4) : '-' },
    { key: 'created_at', label: 'Created', render: (v) => formatDate(v) },
  ]

  const comparisonData = stats ? Object.keys(stats.scores_a).map(dim => ({
    dimension: dim.charAt(0).toUpperCase() + dim.slice(1),
    'Target A': stats.scores_a[dim],
    'Target B': stats.scores_b[dim],
  })) : []

  return (
    <div>
      <Header
        title="A/B Tests"
        subtitle="Compare two LLM targets with statistical significance testing"
        actions={
          <button onClick={() => setShowCreate(true)} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <Plus size={18} /> New Experiment
          </button>
        }
      />

      <DataTable columns={columns} data={tests} onRowClick={setSelectedTest} emptyMessage="No A/B tests yet." />

      <Modal isOpen={showCreate} onClose={() => setShowCreate(false)} title="New A/B Test" size="md">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Experiment Name</label>
            <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="GPT vs Claude comparison" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Target A</label>
              <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.target_a_id} onChange={e => setForm({...form, target_a_id: e.target.value})}>
                <option value="">Select...</option>
                {(targets || []).map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Target B</label>
              <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.target_b_id} onChange={e => setForm({...form, target_b_id: e.target.value})}>
                <option value="">Select...</option>
                {(targets || []).map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
              </select>
            </div>
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
            <label className="block text-sm font-medium text-gray-700 mb-1">Queries (one per line)</label>
            <textarea className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm h-32" value={form.queriesText} onChange={e => setForm({...form, queriesText: e.target.value})} placeholder={"What is machine learning?\nExplain neural networks\nHow does backpropagation work?"} />
          </div>
          <button onClick={handleCreate} disabled={!form.name || !form.target_a_id || !form.target_b_id || !form.queriesText} className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            Start Experiment
          </button>
        </div>
      </Modal>

      <Modal isOpen={!!selectedTest} onClose={() => setSelectedTest(null)} title={selectedTest?.name || 'Experiment Details'} size="lg">
        {selectedTest && stats && (
          <div>
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="text-center p-4 bg-indigo-50 rounded-lg">
                <p className="text-xs text-gray-500 mb-1">{stats.target_a_name}</p>
                <p className="text-2xl font-bold text-indigo-600">{formatScore(stats.avg_a)}</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg flex flex-col justify-center">
                <p className="text-sm font-semibold">{stats.is_significant ? `Winner: ${stats.winner}` : 'No significant difference'}</p>
                <p className="text-xs text-gray-400">p={stats.p_value?.toFixed(4)}</p>
              </div>
              <div className="text-center p-4 bg-emerald-50 rounded-lg">
                <p className="text-xs text-gray-500 mb-1">{stats.target_b_name}</p>
                <p className="text-2xl font-bold text-emerald-600">{formatScore(stats.avg_b)}</p>
              </div>
            </div>

            {comparisonData.length > 0 && (
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-gray-700 mb-3">Score Comparison by Dimension</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={comparisonData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="dimension" />
                    <YAxis domain={[0, 5]} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="Target A" fill={CHART_COLORS[0]} radius={[4, 4, 0, 0]} />
                    <Bar dataKey="Target B" fill={CHART_COLORS[1]} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {stats.confidence_interval && (
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Statistical Details</h4>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div><span className="text-gray-500">Mean Diff:</span> {stats.confidence_interval.mean_diff}</div>
                  <div><span className="text-gray-500">95% CI:</span> [{stats.confidence_interval.lower}, {stats.confidence_interval.upper}]</div>
                  <div><span className="text-gray-500">Significant:</span> {stats.is_significant ? 'Yes' : 'No'}</div>
                </div>
              </div>
            )}
          </div>
        )}
        {selectedTest && !stats && selectedTest.status !== 'completed' && (
          <div className="text-center py-8 text-gray-400">Experiment is still running...</div>
        )}
      </Modal>
    </div>
  )
}
