import request from './request'

export const register = (data) => request.post('/auth/register', data)
export const login = (data) => request.post('/auth/login', data)
export const getUserInfo = () => request.get('/auth/userinfo')
export const changePassword = (data) => request.put('/auth/password', data)
