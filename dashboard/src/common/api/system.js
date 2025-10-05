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
  }
}