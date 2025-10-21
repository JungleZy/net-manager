import axios from '@/config/http/axios.js'

const ResidentProcessApi = {
  /**
   * 获取所有常驻进程列表
   * @returns {Promise}
   */
  getResidentProcessList() {
    return axios({
      method: 'get',
      url: '/api/resident-processes'
    })
  },

  /**
   * 创建单个常驻进程
   * @param {string} name - 进程名称
   * @returns {Promise}
   */
  createResidentProcess(name) {
    return axios({
      method: 'post',
      url: '/api/resident-processes/create',
      data: { name }
    })
  },

  /**
   * 批量创建常驻进程
   * @param {string[]} names - 进程名称数组
   * @returns {Promise}
   */
  batchCreateResidentProcesses(names) {
    return axios({
      method: 'post',
      url: '/api/resident-processes/batch-create',
      data: { names }
    })
  },

  /**
   * 删除常驻进程
   * @param {Object} params - 包含id或name的对象
   * @returns {Promise}
   */
  deleteResidentProcess(params) {
    return axios({
      method: 'post',
      url: '/api/resident-processes/delete',
      data: params
    })
  },

  /**
   * 清空所有常驻进程
   * @returns {Promise}
   */
  clearResidentProcesses() {
    return axios({
      method: 'post',
      url: '/api/resident-processes/clear'
    })
  },

  /**
   * 获取指定设备的常驻进程
   * @param {string} deviceId - 设备ID
   * @returns {Promise}
   */
  getResidentProcessByDevice(deviceId) {
    return axios({
      method: 'get',
      url: '/api/resident-processes/get',
      params: { device_id: deviceId }
    })
  }
}

export default ResidentProcessApi
