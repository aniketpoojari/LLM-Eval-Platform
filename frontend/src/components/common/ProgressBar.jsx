export default function ProgressBar({ current, total, label, color = 'indigo' }) {
  const pct = total > 0 ? Math.round((current / total) * 100) : 0

  const colorMap = {
    indigo: 'bg-indigo-600',
    green: 'bg-green-600',
    red: 'bg-red-600',
    amber: 'bg-amber-500',
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm text-gray-600">{label || `${current} / ${total}`}</span>
        <span className="text-sm font-medium text-gray-900">{pct}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${colorMap[color] || colorMap.indigo}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
