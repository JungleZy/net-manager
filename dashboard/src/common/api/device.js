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
  },
  getDevicesList: () => {
    return axios({
      method: 'get',
      url: '/api/devices'
    })
  },
  getDeviceInfo: (macAddress) => {
    return axios({
      method: 'get',
      url: `/api/devices/${macAddress}`
    })
  },
  updateDeviceType: (macAddress, data) => {
    return axios({
      method: 'put',
      url: `/api/devices/${macAddress}/type`,
      data: data
    })
  }
}

export default DeviceApi