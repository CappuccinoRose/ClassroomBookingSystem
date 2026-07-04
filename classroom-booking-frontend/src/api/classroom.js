import request from './request'

export function getClassroomList(params) {
  return request({
    url: '/classrooms',
    method: 'get',
    params
  })
}

export function getClassroomDetail(id) {
  return request({
    url: `/classrooms/${id}`,
    method: 'get'
  })
}

export function getFreeClassrooms(params) {
  return request({
    url: '/classrooms/free',
    method: 'get',
    params
  })
}

export function createClassroom(data) {
  return request({
    url: '/classrooms',
    method: 'post',
    data
  })
}

export function updateClassroom(id, data) {
  return request({
    url: `/classrooms/${id}`,
    method: 'put',
    data
  })
}

export function deleteClassroom(id) {
  return request({
    url: `/classrooms/${id}`,
    method: 'delete'
  })
}
