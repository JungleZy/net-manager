import localforage from "localforage";
import { PubSub } from "@/common/utils/PubSub";
import { notification } from 'ant-design-vue';

const key = 'updatable';
export const wsCode = {
  SCAN_TASK: "scanTask",
  DEVICE_INFO: "deviceInfo",
  DEVICE_STATUS: "deviceStatus",
  SNMP_DEVICE: "snmpDeviceInfo",
  SNMP_DEVICE_UPDATE: "snmpDeviceUpdate",        // 单设备实时更新
  SNMP_INTERFACE_UPDATE: "snmpInterfaceUpdate",  // 单接口实时更新
  SERVER_PERFORMANCE: "server_performance",       // 服务器性能数据
}
export class Ws {
  constructor() {
    if (!Ws.instance) {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      // const wsUrl = `${wsProtocol}//${window.location.host}/ws`;
      const wsUrl = `${wsProtocol}//${location.hostname}:12344/ws`;
      this.flag = true;
      this.url = wsUrl;
      this.socket = null;
      // 记录上一次设备更新的时间戳（用于计算实时推送频率）
      this.lastDeviceUpdateTime = null;
      this.lastInterfaceUpdateTime = null;
      Ws.instance = this;
    }
    return Ws.instance;
  }

  static getInstance() {
    if (!this.instance) {
      return this.instance = new Ws();
    }
    return this.instance;
  }
  async run() {
    this.socket = new WebSocket(this.url);
    this.socket.onopen = (e) => {
      this.flag = true;
      notification.success({
        key,
        message: `恭喜`,
        description:
          '已连接后端服务器'
      });
    };
    this.socket.onclose = (e) => {
      this.reconnect();
      notification.error({
        key,
        message: `请检查`,
        description:
          '已断开后端服务器！'
      });
    };
    this.socket.onerror = (e) => {
    };
    this.socket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      switch (data.type) {
        case "scanTask":
          localforage.setItem("scanTaskId", data.data.task_id);
          PubSub.publish(wsCode.SCAN_TASK, data.data);
          break;
        case "deviceInfo":
          PubSub.publish(wsCode.DEVICE_INFO, data.data);
          break;
        case "deviceStatus":
          PubSub.publish(wsCode.DEVICE_STATUS, data.data);
          break;
        // 单设备实时更新（快进快出队列模式）
        case "snmpDeviceUpdate":
          this.handleDeviceUpdate(data.data);
          PubSub.publish(wsCode.SNMP_DEVICE_UPDATE, data.data);
          break;

        // 单接口实时更新（快进快出队列模式）
        case "snmpInterfaceUpdate":
          this.handleInterfaceUpdate(data.data);
          PubSub.publish(wsCode.SNMP_INTERFACE_UPDATE, data.data);
          break;

        // 服务器性能数据
        case "server_performance":
          PubSub.publish(wsCode.SERVER_PERFORMANCE, data.data);
          break;

        default:
          break;
      }
    }
  }
  reconnect() {
    const that = this;
    if (this.flag) {
      notification.error({
        key,
        message: `请检查`,
        description:
          '正在重连后端服务器！'
      });
      setTimeout(() => {
        that.run().then();
      }, 5000)
    }
  }

  /**
   * 处理单设备实时更新
   * @param {Object} deviceData - 单个设备数据
   */
  async handleDeviceUpdate(deviceData) {
    console.log('handleDeviceUpdate', deviceData);

    try {
      // 计算更新频率（用于监控）
      const currentTime = Date.now();
      this.lastDeviceUpdateTime = currentTime;

      // 保存单个设备数据（以switch_id为key）
      await this.saveSingleDeviceData(deviceData);

    } catch (error) {
      console.error('设备实时更新处理失败:', error);
    }
  }

  /**
   * 处理单接口实时更新
   * @param {Object} interfaceData - 单个接口数据
   */
  async handleInterfaceUpdate(interfaceData) {
    console.log('handleInterfaceUpdate', interfaceData);
    try {
      // 计算更新频率（用于监控）
      const currentTime = Date.now();
      this.lastInterfaceUpdateTime = currentTime;

      // 保存单个接口数据（以switch_id为key）
      await this.saveSingleInterfaceData(interfaceData);

    } catch (error) {
      console.error('接口实时更新处理失败:', error);
    }
  }

  /**
   * 保存单个设备数据到localforage
   * @param {Object} deviceData - 单个设备数据
   */
  async saveSingleDeviceData(deviceData) {
    try {
      const switchId = deviceData.switch_id;
      if (!switchId) {
        console.warn('设备数据缺少switch_id:', deviceData);
        return;
      }

      // 获取现有的SNMP数据（以switch_id为key）
      let snmpData = await localforage.getItem('snmpData') || {};

      // 如果该switch_id不存在，初始化结构
      if (!snmpData[switchId]) {
        snmpData[switchId] = {
          switch_id: switchId,
          ip: deviceData.ip,
          device_info: null,
          interface_info: null,
          device_update_time: null,
          interface_update_time: null,
          last_update_time: null
        };
      }

      // 更新设备信息
      snmpData[switchId].device_info = deviceData;
      snmpData[switchId].device_update_time = new Date().toISOString();
      snmpData[switchId].last_update_time = new Date().toISOString();
      snmpData[switchId].ip = deviceData.ip; // 更新IP（可能变化）

      // 保存更新后的数据
      await localforage.setItem('snmpData', snmpData);

    } catch (error) {
      console.error('单设备数据保存失败:', error);
    }
  }

  /**
   * 保存单个接口数据到localforage
   * @param {Object} interfaceData - 单个接口数据
   */
  async saveSingleInterfaceData(interfaceData) {
    try {
      const switchId = interfaceData.switch_id;
      if (!switchId) {
        console.warn('接口数据缺少switch_id:', interfaceData);
        return;
      }

      // 获取现有的SNMP数据（以switch_id为key）
      let snmpData = await localforage.getItem('snmpData') || {};

      // 如果该switch_id不存在，初始化结构
      if (!snmpData[switchId]) {
        snmpData[switchId] = {
          switch_id: switchId,
          ip: interfaceData.ip,
          device_info: null,
          interface_info: null,
          device_update_time: null,
          interface_update_time: null,
          last_update_time: null
        };
      }

      // 更新接口信息
      snmpData[switchId].interface_info = interfaceData;
      snmpData[switchId].interface_update_time = new Date().toISOString();
      snmpData[switchId].last_update_time = new Date().toISOString();
      snmpData[switchId].ip = interfaceData.ip; // 更新IP（可能变化）

      // 保存更新后的数据
      await localforage.setItem('snmpData', snmpData);

    } catch (error) {
      console.error('单接口数据保存失败:', error);
    }
  }
}