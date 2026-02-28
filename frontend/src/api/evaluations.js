import client from './client'

export const getEvaluations = () => client.get('/api/evaluations').then(r => r.data)
export const getEvaluation = (id) => client.get(`/api/evaluations/${id}`).then(r => r.data)
export const createEvaluation = (data) => client.post('/api/evaluations', data).then(r => r.data)
export const getEvalResults = (id) => client.get(`/api/evaluations/${id}/results`).then(r => r.data)
export const exportEvaluation = (id, format = 'json') =>
  client.get(`/api/evaluations/${id}/export`, { params: { format } }).then(r => r.data)
