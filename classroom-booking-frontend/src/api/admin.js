import request from './request'

export function getAllReservations(params) {
  return request({
    url: '/admin/reservations',
    method: 'get',
    params
  })
}

export function adminCancelReservation(id) {
  return request({
    url: `/admin/reservations/${id}/cancel`,
    method: 'post'
  })
}

export function restoreReservation(id) {
  return request({
    url: `/admin/reservations/${id}/restore`,
    method: 'post'
  })
}

export function getPendingApprovals(params) {
  return request({
    url: '/admin/approvals/pending',
    method: 'get',
    params
  })
}

export function approveReservation(id, data) {
  return request({
    url: `/admin/approvals/${id}`,
    method: 'post',
    data
  })
}

export function getUsageStatistics(params) {
  return request({
    url: '/admin/statistics/usage',
    method: 'get',
    params
  })
}
