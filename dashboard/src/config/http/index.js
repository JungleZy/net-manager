import axios from 'axios'
import { message, Modal } from 'ant-design-vue'
//创建axios的一个实例
const instance = axios.create({
  baseURL: window.httpUrl, //接口统一域名
  timeout: 180000, //设置超时
  headers: {
    'Content-Type': 'application/json;charset=UTF-8;',
  },
})
//请求拦截器
instance.interceptors.request.use(
  (config) => {
    //若请求方式为post，则将data参数转为JSON字符串
    if (config.method === 'POST') {
      config.data = JSON.stringify(config.data)
    }
    return config
  },
  (error) =>
    // 对请求错误做些什么
    Promise.reject(error),
)

//响应拦截器
instance.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    //响应错误
    if (error.response && error.response.status) {
      let msg = ''
      const status = error.response.status
      switch (status) {
        case 400:
          msg = '请求错误'
          break
        case 401:
          msg = '请求错误'
          break
        case 404:
          msg = '请求地址出错'
          break
        case 408:
          msg = '请求超时'
          break
        case 500:
          msg = '服务器内部错误!'
          break
        case 501:
          msg = '服务未实现!'
          break
        case 502:
          msg = '网关错误!'
          break
        case 503:
          msg = '服务不可用!'
          break
        case 504:
          msg = '网关超时!'
          break
        case 505:
          msg = 'HTTP版本不受支持'
          break
        default:
          msg = '请求失败'
      }
      message.error(msg)
      return Promise.reject(error)
    }
    return Promise.reject(error)
  },
)

export default instance