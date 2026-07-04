import request from './request'

export function getMyReservations(params) {
  return request({
    url: '/reservations/my',
    method: 'get',
    params
  })
}

export function getReservationDetail(id) {
  return request({
    url: `/reservations/${id}`,
    method: 'get'
  })
}

export function createReservation(data) {
  return request({
    url: '/reservations',
    method: 'post',
    data
  })
}

export function updateReservation(id, data) {
  return request({
    url: `/reservations/${id}`,
    method: 'put',
    data
  })
}

export function cancelReservation(id) {
  return request({
    url: `/reservations/${id}/cancel`,
    method: 'post'
  })
}

// Periodic rules
export function getPeriodicRules() {
  return request({
    url: '/reservations/periodic-rules',
    method: 'get'
  })
}

export function createPeriodicRule(data) {
  return request({
    url: '/reservations/periodic-rules',
    method: 'post',
    data
  })
}

export function updatePeriodicRuleStatus(id, status) {
  return request({
    url: `/reservations/periodic-rules/${id}/status`,
    method: 'put',
    data: { status }
  })
}

export function deletePeriodicRule(id) {
  return request({
    url: `/reservations/periodic-rules/${id}`,
    method: 'delete'
  })
}
