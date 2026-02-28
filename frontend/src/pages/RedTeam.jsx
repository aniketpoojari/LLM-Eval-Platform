import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'
import { Plus, Shield } from 'lucide-react'
import Header from '../components/layout/Header'
import DataTable from '../components/common/DataTable'
import Modal from '../components/common/Modal'
import StatusBadge from '../components/common/StatusBadge'
import ProgressBar from '../components/common/ProgressBar'
import { getRedTeamRuns, createRedTeamRun, getRedTeamResults, getCategories } from '../api/redTeam'
import { getTargets } from '../api/targets'
import { formatDate } from '../utils/formatters'
import { ATTACK_CATEGORIES, CHART_COLORS } from '../utils/constants'

export default function RedTeam() {
  const queryClient = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [selectedRun, setSelectedRun] = useState(null)
  const [form, setForm] = useState({ name: '', target_id: '', categories: ATTACK_CATEGORIES.map(c => c.value), max_attacks: 50 })

  const { data: runs } = useQuery({ queryKey: ['redTeamRuns'], queryFn: getRedTeamRuns, refetchInterval: 5000 })
  const { data: targets } = useQuery({ queryKey: ['targets'], queryFn: getTargets })
  const { data: categories } = useQuery({ queryKey: ['categories'], queryFn: getCategories })
  const { data: results } = useQuery({
    queryKey: ['redTeamResults', selectedRun?.id],
    queryFn: () => getRedTeamResults(selectedRun.id),
    enabled: !!selectedRun,
  })

  const createMutation = useMutation({
    mutationFn: createRedTeamRun,
    onSuccess: () => { queryClient.invalidateQueries(['redTeamRuns']); setShowCreate(false) },
  })

  const columns = [
    { key: 'name', label: 'Name' },
    { key: 'status', label: 'Status', render: (v) => <StatusBadge status={v} /> },
    { key: 'total_attacks', label: 'Attacks', render: (v, row) => `${row.completed_attacks}/${v}` },
    { key: 'safety_score', label: 'Safety Score', render: (v) => v !== null ? (
      <span className={v >= 0.8 ? 'text-green-600 font-semibold' : v >= 0.5 ? 'text-amber-600 font-semibold' : 'text-red-600 font-semibold'}>
        {(v * 100).toFixed(0)}%
      </span>
    ) : '-' },
    { key: 'created_at', label: 'Created', render: (v) => formatDate(v) },
  ]

  const categoryBreakdown = results ? (() => {
    const cats = {}
    results.forEach(r => {
      if (!cats[r.category]) cats[r.category] = { safe: 0, unsafe: 0, total: 0 }
      cats[r.category].total++
      if (r.is_safe) cats[r.category].safe++
      else cats[r.category].unsafe++
    })
    return Object.entries(cats).map(([cat, data]) => ({
      category: cat.replace(/_/g, ' '),
      safe: data.safe,
      unsafe: data.unsafe,
      total: data.total,
      safeRate: Math.round((data.safe / data.total) * 100),
    }))
  })() : []

  const pieData = results ? [
    { name: 'Safe', value: results.filter(r => r.is_safe).length },
    { name: 'Unsafe', value: results.filter(r => !r.is_safe).length },
  ] : []

  return (
    <div>
      <Header
        title="Red Team"
        subtitle="Test your LLM targets against 200+ adversarial attacks"
        actions={
          <button onClick={() => setShowCreate(true)} className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
            <Plus size={18} /> New Run
          </button>
        }
      />

      {categories && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
          {categories.map(c => (
            <div key={c.id} className="bg-white rounded-lg border border-gray-200 p-3 text-center">
              <p className="text-lg font-bold text-gray-900">{c.attack_count}</p>
              <p className="text-xs text-gray-500">{c.name}</p>
            </div>
          ))}
        </div>
      )}

      {runs?.some(r => r.status === 'running') && (
        <div className="mb-6">
          {runs.filter(r => r.status === 'running').map(r => (
            <div key={r.id} className="bg-red-50 border border-red-200 rounded-lg p-4 mb-2">
              <p className="text-sm font-medium text-red-800 mb-2">{r.name} - Running</p>
              <ProgressBar current={r.completed_attacks} total={r.total_attacks} color="red" />
            </div>
          ))}
        </div>
      )}

      <DataTable columns={columns} data={runs} onRowClick={setSelectedRun} emptyMessage="No red team runs yet." />

      <Modal isOpen={showCreate} onClose={() => setShowCreate(false)} title="New Red Team Run" size="md">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="Red Team Run" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target</label>
            <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.target_id} onChange={e => setForm({...form, target_id: e.target.value})}>
              <option value="">Select target...</option>
              {(targets || []).map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Attack Categories</label>
            <div className="flex flex-wrap gap-2">
              {ATTACK_CATEGORIES.map(c => (
                <label key={c.value} className="flex items-center gap-1.5 text-sm">
                  <input type="checkbox" checked={form.categories.includes(c.value)} onChange={e => {
                    const cats = e.target.checked ? [...form.categories, c.value] : form.categories.filter(x => x !== c.value)
                    setForm({...form, categories: cats})
                  }} />
                  {c.label}
                </label>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Max Attacks</label>
            <input type="number" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.max_attacks} onChange={e => setForm({...form, max_attacks: parseInt(e.target.value) || 50})} />
          </div>
          <button onClick={() => createMutation.mutate(form)} disabled={!form.name || !form.target_id} className="w-full py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            Start Red Team Run
          </button>
        </div>
      </Modal>

      <Modal isOpen={!!selectedRun} onClose={() => setSelectedRun(null)} title={selectedRun?.name || 'Run Details'} size="lg">
        {selectedRun && (
          <div>
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="flex justify-center">
                {pieData.length > 0 && pieData.some(d => d.value > 0) && (
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                        <Cell fill="#22c55e" />
                        <Cell fill="#ef4444" />
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </div>
              <div className="flex flex-col justify-center space-y-2">
                <p className="text-sm"><span className="font-medium">Status:</span> <StatusBadge status={selectedRun.status} /></p>
                <p className="text-sm"><span className="font-medium">Safety Score:</span> {selectedRun.safety_score !== null ? `${(selectedRun.safety_score * 100).toFixed(0)}%` : '-'}</p>
                <p className="text-sm"><span className="font-medium">Attacks:</span> {selectedRun.completed_attacks}/{selectedRun.total_attacks}</p>
              </div>
            </div>

            {categoryBreakdown.length > 0 && (
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-gray-700 mb-3">Results by Category</h4>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={categoryBreakdown} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="category" type="category" width={120} tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="safe" stackId="a" fill="#22c55e" name="Safe" />
                    <Bar dataKey="unsafe" stackId="a" fill="#ef4444" name="Unsafe" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {results && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-3">Attack Results ({results.length})</h4>
                <div className="space-y-2 max-h-64 overflow-auto">
                  {results.map(r => (
                    <div key={r.id} className={`border rounded-lg p-3 ${r.is_safe ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
                      <div className="flex justify-between items-start mb-1">
                        <span className="text-xs font-medium text-gray-500">{r.category} / {r.subcategory}</span>
                        <span className={`text-xs font-semibold ${r.is_safe ? 'text-green-600' : 'text-red-600'}`}>{r.is_safe ? 'SAFE' : 'UNSAFE'}</span>
                      </div>
                      <p className="text-sm text-gray-800 mb-1">{r.attack_name}</p>
                      {r.explanation && <p className="text-xs text-gray-500">{r.explanation}</p>}
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
