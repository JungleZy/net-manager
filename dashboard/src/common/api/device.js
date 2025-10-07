import axios from '@/config/http/axios.js'

const DeviceApi = {
  /**
   * 创建设备
   * @param {Object} deviceData - 设备数据
   * @returns {Promise}
   */
  createDevice(deviceData) {
    return axios({
      method: 'post',
      url: '/api/devices/create',
      data: deviceData
    })
  },

  /**
   * 更新设备
   * @param {Object} deviceData - 设备数据
   * @returns {Promise}
   */
  updateDevice(deviceData) {
    return axios({
      method: 'post',
      url: '/api/devices/update',
      data: deviceData
    })
  },

  /**
   * 删除设备
   * @param {Object} params - 包含mac_address的对象
   * @returns {Promise}
   */
  deleteDevice(params) {
    return axios({
      method: 'post',
      url: '/api/devices/delete',
      data: params
    })
  }
}

export default DeviceApi