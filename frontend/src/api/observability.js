import client from './client'

export const getSummary = () => client.get('/api/observability/summary').then(r => r.data)
export const getTokenUsage = (days = 30) =>
  client.get('/api/observability/tokens', { params: { days } }).then(r => r.data)
export const getCosts = (days = 30) =>
  client.get('/api/observability/costs', { params: { days } }).then(r => r.data)
export const getLatency = (days = 30) =>
  client.get('/api/observability/latency', { params: { days } }).then(r => r.data)
export const getScoreTrends = (days = 30) =>
  client.get('/api/observability/scores', { params: { days } }).then(r => r.data)
