/**
 * SNMP设备数据存储工具类
 * 使用localforage管理SNMP设备数据的持久化存储
 * 数据结构：以switch_id为主键，每个交换机包含device_info和interface_info
 */
import localforage from 'localforage';

export class SNMPStorage {
  /**
   * 获取所有SNMP数据（统一存储，以switch_id为主键）
   * @returns {Promise<Object>} SNMP数据对象，key为switch_id
   */
  static async getAllData() {
    try {
      const data = await localforage.getItem('snmpData');
      return data || {};
    } catch (error) {
      console.error('获取SNMP数据失败:', error);
      return {};
    }
  }

  /**
   * 获取所有设备信息（兼容旧接口）
   * @returns {Promise<Object>} 设备数据对象
   */
  static async getAllDevices() {
    return await this.getAllData();
  }

  /**
   * 根据switch_id获取交换机数据
   * @param {string|number} switchId - 交换机ID
   * @returns {Promise<Object|null>} 交换机完整数据或null
   */
  static async getSwitchData(switchId) {
    try {
      const data = await this.getAllData();
      return data[switchId] || null;
    } catch (error) {
      console.error('获取交换机数据失败:', error);
      return null;
    }
  }

  /**
   * 根据switch_id获取设备信息
   * @param {string|number} switchId - 交换机ID
   * @returns {Promise<Object|null>} 设备信息或null
   */
  static async getDeviceInfo(switchId) {
    try {
      const switchData = await this.getSwitchData(switchId);
      return switchData?.device_info || null;
    } catch (error) {
      console.error('获取设备信息失败:', error);
      return null;
    }
  }

  /**
   * 根据switch_id获取接口信息
   * @param {string|number} switchId - 交换机ID
   * @returns {Promise<Object|null>} 接口信息或null
   */
  static async getInterfaceInfo(switchId) {
    try {
      const switchData = await this.getSwitchData(switchId);
      return switchData?.interface_info || null;
    } catch (error) {
      console.error('获取接口信息失败:', error);
      return null;
    }
  }

  /**
   * 根据IP地址查找交换机ID
   * @param {string} ip - IP地址
   * @returns {Promise<string|null>} 交换机ID或null
   */
  static async findSwitchIdByIp(ip) {
    try {
      const data = await this.getAllData();
      const entry = Object.entries(data).find(([_, sw]) => sw.ip === ip);
      return entry ? entry[0] : null;
    } catch (error) {
      console.error('查找交换机ID失败:', error);
      return null;
    }
  }

  /**
   * 兼容旧接口：根据IP或switch_id获取设备数据
   * @param {string} key - IP地址或switch_id
   * @returns {Promise<Object|null>} 设备数据或null
   */
  static async getDevice(key) {
    try {
      const data = await this.getAllData();
      // 先尝试作为switch_id
      if (data[key]) {
        return data[key];
      }
      // 再尝试作为IP查找
      const switchId = await this.findSwitchIdByIp(key);
      return switchId ? data[switchId] : null;
    } catch (error) {
      console.error('获取设备数据失败:', error);
      return null;
    }
  }

  /**
   * 获取所有在线设备（设备信息或接口信息任一在线即视为在线）
   * @returns {Promise<Array>} 在线设备数组
   */
  static async getOnlineDevices() {
    try {
      const data = await this.getAllData();
      return Object.values(data).filter(sw =>
        sw.device_info?.type === 'success' || sw.interface_info?.type === 'success'
      );
    } catch (error) {
      console.error('获取在线设备失败:', error);
      return [];
    }
  }

  /**
   * 获取所有离线设备（设备信息和接口信息都离线或都不存在）
   * @returns {Promise<Array>} 离线设备数组
   */
  static async getOfflineDevices() {
    try {
      const data = await this.getAllData();
      return Object.values(data).filter(sw =>
        sw.device_info?.type === 'error' && sw.interface_info?.type === 'error'
      );
    } catch (error) {
      console.error('获取离线设备失败:', error);
      return [];
    }
  }

  /**
   * 获取统计信息
   * @returns {Promise<Object|null>} 统计信息或null
   */
  static async getSummary() {
    try {
      const summary = await localforage.getItem('snmpSummary');
      return summary || null;
    } catch (error) {
      console.error('获取统计信息失败:', error);
      return null;
    }
  }

  /**
   * 清除所有SNMP数据
   * @returns {Promise<void>}
   */
  static async clearAll() {
    try {
      await localforage.removeItem('snmpData');
      await localforage.removeItem('snmpSummary');
      console.log('SNMP数据已清除');
    } catch (error) {
      console.error('清除SNMP数据失败:', error);
    }
  }

  /**
   * 获取设备数量统计
   * @returns {Promise<Object>} 包含总数、在线数、离线数的对象
   */
  static async getDeviceCount() {
    try {
      const data = await this.getAllData();
      const switches = Object.values(data);
      const onlineCount = switches.filter(sw =>
        sw.device_info?.type === 'success' || sw.interface_info?.type === 'success'
      ).length;
      const offlineCount = switches.filter(sw =>
        sw.device_info?.type === 'error' && sw.interface_info?.type === 'error'
      ).length;

      return {
        total: switches.length,
        online: onlineCount,
        offline: offlineCount
      };
    } catch (error) {
      console.error('获取设备统计失败:', error);
      return { total: 0, online: 0, offline: 0 };
    }
  }

  /**
   * 根据状态类型筛选
   * @param {string} type - 状态类型 'success' 或 'error'
   * @returns {Promise<Array>} 设备数组
   */
  static async getDevicesByType(type) {
    try {
      if (type === 'success') {
        return await this.getOnlineDevices();
      } else if (type === 'error') {
        return await this.getOfflineDevices();
      }
      return [];
    } catch (error) {
      console.error('筛选设备失败:', error);
      return [];
    }
  }

  /**
   * 搜索设备
   * @param {string} searchText - 搜索文本（匹配IP、设备名称等）
   * @returns {Promise<Array>} 匹配的设备数组
   */
  static async searchDevices(searchText) {
    try {
      const data = await this.getAllData();
      const switches = Object.values(data);

      if (!searchText) {
        return switches;
      }

      const text = searchText.toLowerCase();
      return switches.filter(sw => {
        return (
          (sw.ip && sw.ip.toLowerCase().includes(text)) ||
          (sw.device_info?.device_info?.sysName &&
            sw.device_info.device_info.sysName.toLowerCase().includes(text)) ||
          (sw.device_info?.device_info?.sysDescr &&
            sw.device_info.device_info.sysDescr.toLowerCase().includes(text))
        );
      });
    } catch (error) {
      console.error('搜索设备失败:', error);
      return [];
    }
  }

  /**
   * 获取设备最后更新时间
   * @param {string|number} switchId - 交换机ID
   * @returns {Promise<string|null>} ISO格式的时间字符串或null
   */
  static async getDeviceUpdateTime(switchId) {
    try {
      const switchData = await this.getSwitchData(switchId);
      return switchData?.last_update_time || switchData?.device_update_time || null;
    } catch (error) {
      console.error('获取设备更新时间失败:', error);
      return null;
    }
  }

  /**
   * 检查设备是否在线
   * @param {string|number} switchId - 交换机ID
   * @returns {Promise<boolean>} 是否在线
   */
  static async isDeviceOnline(switchId) {
    try {
      const switchData = await this.getSwitchData(switchId);
      return switchData ?
        (switchData.device_info?.type === 'success' ||
          switchData.interface_info?.type === 'success') : false;
    } catch (error) {
      console.error('检查设备在线状态失败:', error);
      return false;
    }
  }

  /**
   * 构建设备状态映射（以switch_id为key）
   * @returns {Promise<Object>} 状态映射对象
   */
  static async buildStatusMap() {
    try {
      const data = await this.getAllData();
      const statusMap = {};

      Object.entries(data).forEach(([switchId, switchData]) => {
        // 优先使用设备信息的状态，如果设备信息不存在则使用接口信息的状态
        const deviceStatus = switchData.device_info?.type;
        const interfaceStatus = switchData.interface_info?.type;

        statusMap[switchId] = {
          type: deviceStatus || interfaceStatus || 'unknown',
          updateTime: switchData.last_update_time || switchData.device_update_time,
          error: switchData.device_info?.error || switchData.interface_info?.error,
          device_info: switchData.device_info?.device_info || {},
          interface_info: switchData.interface_info?.interface_info || []
        };
      });

      return statusMap;
    } catch (error) {
      console.error('构建状态映射失败:', error);
      return {};
    }
  }
}

export default SNMPStorage;
