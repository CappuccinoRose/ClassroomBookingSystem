import request from './request'

export const listAllReservations = (params) => request.get('/admin/reservations', { params })
export const adminCancelReservation = (id) => request.post(`/admin/reservations/${id}/cancel`)
export const restoreReservation = (id) => request.post(`/admin/reservations/${id}/restore`)
export const listPendingApprovals = (params) => request.get('/admin/approvals/pending', { params })
export const approveReservation = (id, data) => request.post(`/admin/approvals/${id}`, data)
export const getStatistics = (params) => request.get('/admin/statistics/usage', { params })
