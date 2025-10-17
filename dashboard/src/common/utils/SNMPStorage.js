/**
 * SNMP设备数据存储工具类
 * 使用localforage管理SNMP设备数据的持久化存储
 */
import localforage from 'localforage';

export class SNMPStorage {
  /**
   * 获取所有SNMP设备数据
   * @returns {Promise<Object>} 设备数据对象，key为IP或switch_id
   */
  static async getAllDevices() {
    try {
      const devices = await localforage.getItem('snmpDevices');
      return devices || {};
    } catch (error) {
      console.error('获取SNMP设备数据失败:', error);
      return {};
    }
  }

  /**
   * 根据IP或switch_id获取单个设备数据
   * @param {string} key - 设备IP或switch_id
   * @returns {Promise<Object|null>} 设备数据或null
   */
  static async getDevice(key) {
    try {
      const devices = await this.getAllDevices();
      return devices[key] || null;
    } catch (error) {
      console.error('获取设备数据失败:', error);
      return null;
    }
  }

  /**
   * 获取所有在线设备
   * @returns {Promise<Array>} 在线设备数组
   */
  static async getOnlineDevices() {
    try {
      const devices = await this.getAllDevices();
      return Object.values(devices).filter(device => device.type === 'success');
    } catch (error) {
      console.error('获取在线设备失败:', error);
      return [];
    }
  }

  /**
   * 获取所有离线设备
   * @returns {Promise<Array>} 离线设备数组
   */
  static async getOfflineDevices() {
    try {
      const devices = await this.getAllDevices();
      return Object.values(devices).filter(device => device.type === 'error');
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
   * 清除所有SNMP设备数据
   * @returns {Promise<void>}
   */
  static async clearAll() {
    try {
      await localforage.removeItem('snmpDevices');
      await localforage.removeItem('snmpSummary');
      console.log('SNMP设备数据已清除');
    } catch (error) {
      console.error('清除SNMP设备数据失败:', error);
    }
  }

  /**
   * 获取设备数量统计
   * @returns {Promise<Object>} 包含总数、在线数、离线数的对象
   */
  static async getDeviceCount() {
    try {
      const devices = await this.getAllDevices();
      const deviceArray = Object.values(devices);
      const onlineCount = deviceArray.filter(d => d.type === 'success').length;
      const offlineCount = deviceArray.filter(d => d.type === 'error').length;

      return {
        total: deviceArray.length,
        online: onlineCount,
        offline: offlineCount
      };
    } catch (error) {
      console.error('获取设备统计失败:', error);
      return { total: 0, online: 0, offline: 0 };
    }
  }

  /**
   * 根据设备类型筛选
   * @param {string} type - 设备类型 'success' 或 'error'
   * @returns {Promise<Array>} 设备数组
   */
  static async getDevicesByType(type) {
    try {
      const devices = await this.getAllDevices();
      return Object.values(devices).filter(device => device.type === type);
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
      const devices = await this.getAllDevices();
      const deviceArray = Object.values(devices);

      if (!searchText) {
        return deviceArray;
      }

      const text = searchText.toLowerCase();
      return deviceArray.filter(device => {
        return (
          (device.ip && device.ip.toLowerCase().includes(text)) ||
          (device.device_info && device.device_info.name &&
            device.device_info.name.toLowerCase().includes(text)) ||
          (device.device_info && device.device_info.description &&
            device.device_info.description.toLowerCase().includes(text))
        );
      });
    } catch (error) {
      console.error('搜索设备失败:', error);
      return [];
    }
  }

  /**
   * 获取设备最后更新时间
   * @param {string} key - 设备IP或switch_id
   * @returns {Promise<string|null>} ISO格式的时间字符串或null
   */
  static async getDeviceUpdateTime(key) {
    try {
      const device = await this.getDevice(key);
      return device ? device.updateTime : null;
    } catch (error) {
      console.error('获取设备更新时间失败:', error);
      return null;
    }
  }

  /**
   * 检查设备是否在线
   * @param {string} key - 设备IP或switch_id
   * @returns {Promise<boolean>} 是否在线
   */
  static async isDeviceOnline(key) {
    try {
      const device = await this.getDevice(key);
      return device ? device.type === 'success' : false;
    } catch (error) {
      console.error('检查设备在线状态失败:', error);
      return false;
    }
  }
}

export default SNMPStorage;
