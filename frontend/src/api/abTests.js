import client from './client'

export const getABTests = () => client.get('/api/ab-tests').then(r => r.data)
export const getABTest = (id) => client.get(`/api/ab-tests/${id}`).then(r => r.data)
export const createABTest = (data) => client.post('/api/ab-tests', data).then(r => r.data)
export const getABResults = (id) => client.get(`/api/ab-tests/${id}/results`).then(r => r.data)
export const getABStats = (id) => client.get(`/api/ab-tests/${id}/stats`).then(r => r.data)
