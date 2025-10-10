import axios from '@/config/http/axios.js'

const SwitchApi = {
  /**
   * 创建交换机
   * @param {Object} switchData - 交换机数据
   * @returns {Promise}
   */
  createSwitch(switchData) {
    return axios({
      method: 'post',
      url: '/api/switches/create',
      data: switchData
    })
  },

  /**
   * 更新交换机
   * @param {Object} switchData - 交换机数据
   * @returns {Promise}
   */
  updateSwitch(switchData) {
    return axios({
      method: 'post',
      url: '/api/switches/update',
      data: switchData
    })
  },

  /**
   * 删除交换机
   * @param {Object} params - 包含id的对象
   * @returns {Promise}
   */
  deleteSwitch(params) {
    return axios({
      method: 'post',
      url: '/api/switches/delete',
      data: params
    })
  },

  /**
   * 获取所有交换机列表
   * @returns {Promise}
   */
  getSwitchesList() {
    return axios({
      method: 'get',
      url: '/api/switches'
    })
  },

  /**
   * 根据ID获取交换机信息
   * @param {Number} switchId - 交换机ID
   * @returns {Promise}
   */
  getSwitchInfo(switchId) {
    return axios({
      method: 'get',
      url: `/api/switches/${switchId}`
    })
  }
}

export default SwitchApi