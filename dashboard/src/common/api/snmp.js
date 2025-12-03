import axios from '@/config/http/axios.js'

const SnmpApi = {
  getHistory(switchId, { limit = 100, offset = 0, poll_type } = {}) {
    return axios({
      method: 'get',
      url: `/api/snmp/history/${switchId}`,
      params: { limit, offset, poll_type }
    })
  },

  clearHistory(switchId) {
    return axios({
      method: 'post',
      url: '/api/snmp/history/clear',
      data: switchId ? { switch_id: switchId } : {}
    })
  }
}

export default SnmpApi
