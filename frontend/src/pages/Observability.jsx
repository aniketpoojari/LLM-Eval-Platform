import { useQuery } from '@tanstack/react-query'
import {
  LineChart, Line, BarChart, Bar, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { Activity, Zap, DollarSign, Clock } from 'lucide-react'
import Header from '../components/layout/Header'
import ScoreCard from '../components/common/ScoreCard'
import { getSummary, getTokenUsage, getCosts, getLatency, getScoreTrends } from '../api/observability'
import { formatCost, formatNumber, formatLatency } from '../utils/formatters'
import { CHART_COLORS } from '../utils/constants'

export default function Observability() {
  const { data: summary } = useQuery({ queryKey: ['summary'], queryFn: getSummary })
  const { data: tokens } = useQuery({ queryKey: ['tokens'], queryFn: () => getTokenUsage(30) })
  const { data: costs } = useQuery({ queryKey: ['costs'], queryFn: () => getCosts(30) })
  const { data: latency } = useQuery({ queryKey: ['latency'], queryFn: () => getLatency(30) })
  const { data: scores } = useQuery({ queryKey: ['scoreTrends'], queryFn: () => getScoreTrends(30) })

  return (
    <div>
      <Header title="Observability" subtitle="Monitor token usage, latency, costs, and evaluation trends" />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <ScoreCard title="Total Queries" value={formatNumber(summary?.total_queries_processed)} icon={Activity} color="indigo" />
        <ScoreCard title="Total Tokens" value={formatNumber(summary?.total_tokens)} icon={Zap} color="amber" />
        <ScoreCard title="Total Cost" value={formatCost(summary?.total_cost)} icon={DollarSign} color="green" />
        <ScoreCard title="Avg Latency" value={formatLatency(summary?.avg_latency_ms)} icon={Clock} color="blue" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Token Usage Over Time</h3>
          {tokens && tokens.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={tokens}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="input_tokens" stackId="1" stroke={CHART_COLORS[0]} fill={CHART_COLORS[0]} fillOpacity={0.4} name="Input" />
                <Area type="monotone" dataKey="output_tokens" stackId="1" stroke={CHART_COLORS[1]} fill={CHART_COLORS[1]} fillOpacity={0.4} name="Output" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[280px] flex items-center justify-center text-gray-400">No data yet</div>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Daily Cost</h3>
          {costs?.daily_costs && costs.daily_costs.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={costs.daily_costs}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v) => formatCost(v)} />
                <Bar dataKey="cost" fill={CHART_COLORS[1]} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[280px] flex items-center justify-center text-gray-400">No data yet</div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Latency Trends</h3>
          {latency && latency.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={latency}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v) => `${Math.round(v)}ms`} />
                <Legend />
                <Line type="monotone" dataKey="avg_latency" stroke={CHART_COLORS[4]} strokeWidth={2} name="Avg" dot={false} />
                <Line type="monotone" dataKey="max_latency" stroke={CHART_COLORS[3]} strokeWidth={1} strokeDasharray="5 5" name="Max" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[280px] flex items-center justify-center text-gray-400">No data yet</div>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Evaluation Score Trends</h3>
          {scores && scores.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={scores}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 5]} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Line type="monotone" dataKey="avg_score" stroke={CHART_COLORS[0]} strokeWidth={2} dot={{ fill: CHART_COLORS[0], r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[280px] flex items-center justify-center text-gray-400">No data yet</div>
          )}
        </div>
      </div>

      {costs?.cost_by_source && Object.keys(costs.cost_by_source).length > 0 && (
        <div className="mt-6 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Cost by Source</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(costs.cost_by_source).map(([source, cost]) => (
              <div key={source} className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-lg font-bold text-gray-900">{formatCost(cost)}</p>
                <p className="text-xs text-gray-500 capitalize">{source.replace(/_/g, ' ')}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
