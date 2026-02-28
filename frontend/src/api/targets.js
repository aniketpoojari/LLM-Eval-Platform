import client from './client'

export const getTargets = () => client.get('/api/targets').then(r => r.data)
export const getTarget = (id) => client.get(`/api/targets/${id}`).then(r => r.data)
export const createTarget = (data) => client.post('/api/targets', data).then(r => r.data)
export const updateTarget = (id, data) => client.put(`/api/targets/${id}`, data).then(r => r.data)
export const deleteTarget = (id) => client.delete(`/api/targets/${id}`).then(r => r.data)
export const testTarget = (id, data) => client.post(`/api/targets/${id}/test`, data).then(r => r.data)
