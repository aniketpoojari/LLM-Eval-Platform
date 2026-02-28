import client from './client'

export const getRedTeamRuns = () => client.get('/api/red-team/runs').then(r => r.data)
export const getRedTeamRun = (id) => client.get(`/api/red-team/runs/${id}`).then(r => r.data)
export const createRedTeamRun = (data) => client.post('/api/red-team/runs', data).then(r => r.data)
export const getRedTeamResults = (id) => client.get(`/api/red-team/runs/${id}/results`).then(r => r.data)
export const getAttacks = (category) =>
  client.get('/api/red-team/attacks', { params: category ? { category } : {} }).then(r => r.data)
export const getCategories = () => client.get('/api/red-team/categories').then(r => r.data)
