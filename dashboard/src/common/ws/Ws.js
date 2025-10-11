export const wsCode = {
  SCAN_TASK: "scanTask",
}
export class Ws {
  constructor() {
    if (!Ws.instance) {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      // const wsUrl = `${wsProtocol}//${window.location.host}/ws`;
      const wsUrl = `${wsProtocol}//10.10.0.212:12344/ws`;
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
    };
    this.socket.onclose = (e) => {
      this.reconnect();
    };
    this.socket.onerror = (e) => {
    };
    this.socket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      console.log(data);
      switch (data.type) {
        case "scanTask":
          PubSub.publish(wsCode.SCAN_TASK, data.data);
          break;
        default:
          break;
      }
    }
  }
  reconnect() {
    const that = this;
    if (this.flag) {
      setTimeout(() => {
        that.run().then();
      }, 3000)
    }
  }
}