import localforage from "localforage";
import { PubSub } from "@/common/utils/PubSub";
import { notification } from 'ant-design-vue';
const [api, contextHolder] = notification.useNotification();

const key = 'updatable';
export const wsCode = {
  SCAN_TASK: "scanTask",
  DEVICE_INFO: "deviceInfo",
  DEVICE_STATUS: "deviceStatus",
  SNMP_DEVICE: "snmpDeviceInfo",
  SNMP_DEVICE_BATCH: "snmpDeviceBatch"
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
        case "snmpDeviceInfo":
          console.log("snmpDeviceInfo", data);
          PubSub.publish(wsCode.SNMP_DEVICE, data.data);
          break;
        case "snmpDeviceBatch":
          this.saveSNMPDeviceData(data.data, data.summary);
          PubSub.publish(wsCode.SNMP_DEVICE_BATCH, data.data);
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
   * 保存SNMP设备数据到localforage
   * @param {Array} devices - 设备数据数组
   * @param {Object} summary - 统计信息
   */
  async saveSNMPDeviceData(devices, summary) {
    try {
      // 获取现有的SNMP设备数据
      let snmpDevices = await localforage.getItem('snmpDevices') || {};

      // 更新每个设备的数据
      devices.forEach(device => {
        const key = device.ip || device.switch_id;
        if (key) {
          snmpDevices[key] = {
            ...device,
            updateTime: new Date().toISOString(),
            timestamp: Date.now()
          };
        }
      });

      // 保存更新后的数据
      await localforage.setItem('snmpDevices', snmpDevices);

      // 保存最新的统计信息
      if (summary) {
        await localforage.setItem('snmpSummary', {
          ...summary,
          lastUpdateTime: new Date().toISOString(),
          timestamp: Date.now()
        });
      }

    } catch (error) {
      console.error('SNMP设备数据保存失败:', error);
    }
  }
}