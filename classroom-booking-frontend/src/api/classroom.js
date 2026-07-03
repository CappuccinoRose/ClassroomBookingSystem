import request from './request'

export const listClassrooms = (params) => request.get('/classrooms', { params })
export const getClassroom = (id) => request.get(`/classrooms/${id}`)
export const createClassroom = (data) => request.post('/classrooms', data)
export const updateClassroom = (id, data) => request.put(`/classrooms/${id}`, data)
export const deleteClassroom = (id) => request.delete(`/classrooms/${id}`)
export const findFreeClassrooms = (params) => request.get('/classrooms/free', { params })
