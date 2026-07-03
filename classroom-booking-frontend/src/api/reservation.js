import request from './request'

export const listMyReservations = (params) => request.get('/reservations/my', { params })
export const getReservation = (id) => request.get(`/reservations/${id}`)
export const createReservation = (data) => request.post('/reservations', data)
export const updateReservation = (id, data) => request.put(`/reservations/${id}`, data)
export const cancelReservation = (id) => request.post(`/reservations/${id}/cancel`)

export const listPeriodicRules = () => request.get('/reservations/periodic-rules')
export const createPeriodicRule = (data) => request.post('/reservations/periodic-rules', data)
export const updateRuleStatus = (id, status) => request.put(`/reservations/periodic-rules/${id}/status`, { status })
export const deleteRule = (id) => request.delete(`/reservations/periodic-rules/${id}`)
