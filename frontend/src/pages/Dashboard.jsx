import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'
import { ClipboardCheck, Shield, GitCompare, Activity, DollarSign, Zap } from 'lucide-react'
import Header from '../components/layout/Header'
import ScoreCard from '../components/common/ScoreCard'
import { getSummary, getScoreTrends, getCosts } from '../api/observability'
import { getEvaluations } from '../api/evaluations'
import { getRedTeamRuns } from '../api/redTeam'
import { formatScore, formatCost, formatNumber, formatDate } from '../utils/formatters'
import { CHART_COLORS } from '../utils/constants'

export default function Dashboard() {
  const { data: summary } = useQuery({ queryKey: ['summary'], queryFn: getSummary })
  const { data: scores } = useQuery({ queryKey: ['scoreTrends'], queryFn: () => getScoreTrends(30) })
  const { data: costs } = useQuery({ queryKey: ['costs'], queryFn: () => getCosts(30) })
  const { data: evals } = useQuery({ queryKey: ['evaluations'], queryFn: getEvaluations })
  const { data: redTeamRuns } = useQuery({ queryKey: ['redTeamRuns'], queryFn: getRedTeamRuns })

  const recentEvals = (evals || []).slice(0, 5)
  const recentRedTeam = (redTeamRuns || []).slice(0, 5)

  return (
    <div>
      <Header title="Dashboard" subtitle="Overview of your LLM evaluation activities" />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-8">
        <ScoreCard
          title="Evaluations"
          value={summary?.total_evaluations || 0}
          icon={ClipboardCheck}
          color="indigo"
        />
        <ScoreCard
          title="Red Team Runs"
          value={summary?.total_red_team_runs || 0}
          icon={Shield}
          color="red"
        />
        <ScoreCard
          title="A/B Tests"
          value={summary?.total_ab_tests || 0}
          icon={GitCompare}
          color="blue"
        />
        <ScoreCard
          title="Queries Processed"
          value={formatNumber(summary?.total_queries_processed)}
          icon={Activity}
          color="green"
        />
        <ScoreCard
          title="Total Tokens"
          value={formatNumber(summary?.total_tokens)}
          icon={Zap}
          color="amber"
        />
        <ScoreCard
          title="Total Cost"
          value={formatCost(summary?.total_cost)}
          icon={DollarSign}
          color="green"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Score Trends</h3>
          {scores && scores.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={scores}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 5]} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Line type="monotone" dataKey="avg_score" stroke={CHART_COLORS[0]} strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[250px] flex items-center justify-center text-gray-400">No data yet</div>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Daily Cost</h3>
          {costs?.daily_costs && costs.daily_costs.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={costs.daily_costs}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip formatter={(v) => formatCost(v)} />
                <Bar dataKey="cost" fill={CHART_COLORS[1]} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[250px] flex items-center justify-center text-gray-400">No data yet</div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Recent Evaluations</h3>
          {recentEvals.length > 0 ? (
            <div className="space-y-3">
              {recentEvals.map((e) => (
                <div key={e.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{e.name}</p>
                    <p className="text-xs text-gray-400">{formatDate(e.created_at)}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold">{formatScore(e.avg_score)}</p>
                    <p className="text-xs text-gray-400">{e.status}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">No evaluations yet</p>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Recent Red Team Runs</h3>
          {recentRedTeam.length > 0 ? (
            <div className="space-y-3">
              {recentRedTeam.map((r) => (
                <div key={r.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{r.name}</p>
                    <p className="text-xs text-gray-400">{formatDate(r.created_at)}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold">{r.safety_score !== null ? `${(r.safety_score * 100).toFixed(0)}%` : '-'}</p>
                    <p className="text-xs text-gray-400">{r.status}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">No red team runs yet</p>
          )}
        </div>
      </div>
    </div>
  )
}
