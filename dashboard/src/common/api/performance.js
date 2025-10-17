import axios from '@/config/http/axios.js'

const PerformanceApi = {
  /**
   * 获取当前服务器性能数据
   * @returns {Promise}
   */
  getCurrentPerformance() {
    return axios({
      method: 'get',
      url: '/api/performance'
    })
  }
}

export default PerformanceApi
