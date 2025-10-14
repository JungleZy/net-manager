import axios from '@/config/http/axios.js'

const TopologyApi = {
  /**
   * 创建拓扑图
   * @param {Object} content - 拓扑图内容
   * @returns {Promise}
   */
  createTopology(content) {
    return axios({
      method: 'post',
      url: '/api/topologies/create',
      data: { content }
    })
  },

  /**
   * 更新拓扑图
   * @param {Number} id - 拓扑图ID
   * @param {Object} content - 拓扑图内容
   * @returns {Promise}
   */
  updateTopology(id, content) {
    return axios({
      method: 'post',
      url: '/api/topologies/update',
      data: { id, content }
    })
  },

  /**
   * 删除拓扑图
   * @param {Number} id - 拓扑图ID
   * @returns {Promise}
   */
  deleteTopology(id) {
    return axios({
      method: 'post',
      url: '/api/topologies/delete',
      data: { id }
    })
  },

  /**
   * 获取所有拓扑图
   * @returns {Promise}
   */
  getTopologiesList() {
    return axios({
      method: 'get',
      url: '/api/topologies'
    })
  },

  /**
   * 获取最新拓扑图
   * @returns {Promise}
   */
  getLatestTopology() {
    return axios({
      method: 'get',
      url: '/api/topologies/latest'
    })
  },

  /**
   * 根据ID获取拓扑图
   * @param {Number} id - 拓扑图ID
   * @returns {Promise}
   */
  getTopologyById(id) {
    return axios({
      method: 'get',
      url: `/api/topologies/${id}`
    })
  }
}

export default TopologyApi
