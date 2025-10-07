import axios from "../../config/http/axios.js"
export default {
  getSystemsList: () => {
    return axios({
      method: 'get',
      url: '/api/systems'
    })
  },
  getSystemInfo: (macAddress) => {
    return axios({
      method: 'get',
      url: `/api/systems/${macAddress}`
    })
  },
  updateSystemType: (macAddress, data) => {
    return axios({
      method: 'put',
      url: `/api/systems/${macAddress}/type`,
      data: data
    })
  }
}