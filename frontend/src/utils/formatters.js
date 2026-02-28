export function formatScore(score) {
  if (score === null || score === undefined) return '-'
  return score.toFixed(2)
}

export function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatCost(cost) {
  if (cost === null || cost === undefined) return '$0.00'
  return `$${cost.toFixed(4)}`
}

export function formatNumber(num) {
  if (num === null || num === undefined) return '0'
  return num.toLocaleString()
}

export function formatLatency(ms) {
  if (ms === null || ms === undefined) return '-'
  if (ms < 1000) return `${Math.round(ms)}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

export function getScoreColor(score) {
  if (score >= 4) return 'text-green-600'
  if (score >= 3) return 'text-amber-600'
  return 'text-red-600'
}

export function getSafetyColor(score) {
  if (score >= 0.8) return 'text-green-600'
  if (score >= 0.5) return 'text-amber-600'
  return 'text-red-600'
}
