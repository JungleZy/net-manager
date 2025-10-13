import { BaseCustomNode, BaseCustomNodeModel } from './BaseCustomNode';
import { h } from '@logicflow/core';

class ServerNode extends BaseCustomNode {
  getSVGContent() {
    // 获取节点状态以确定颜色
    const { model } = this.props;
    const { status } = model.properties;

    // 根据status设置颜色
    const primaryColor = status === 'offline' ? '#ffffff' : '#B5D6FB';
    const secondaryColor = status === 'offline' ? '#999999' : '#1677FF';
    const whiteColor = '#FFFFFF'; // 白色保持不变
    return [
      h('path', {
        d: "M470.9 954.6c-1.2 0-2.3-0.3-3.4-0.9l-240-132.2c-2.2-1.2-3.6-3.6-3.6-6.1V270.6c0-2.5 1.3-4.7 3.4-6L546.9 70.4c1.1-0.7 2.4-1 3.6-1 1.2 0 2.4 0.3 3.4 0.9l242.6 136.9c2.2 1.2 3.6 3.6 3.6 6.1v552.8c0 2.5-1.4 4.9-3.6 6.1L474.4 953.7c-1.1 0.6-2.3 0.9-3.5 0.9z",
        fill: secondaryColor
      }),
      h('path', {
        d: "M550.5 76.4l242.6 136.9v552.8L470.9 947.6l-240-132.2V270.6L550.5 76.4m0-14c-2.5 0-5 0.7-7.3 2L223.6 258.6c-4.2 2.5-6.7 7.1-6.7 12v544.8c0 5.1 2.8 9.8 7.3 12.3l240 132.2c2.1 1.2 4.4 1.7 6.8 1.7 2.4 0 4.7-0.6 6.9-1.8L800 778.3c4.4-2.5 7.1-7.2 7.1-12.2V213.3c0-5.1-2.7-9.7-7.1-12.2L557.4 64.2c-2.1-1.2-4.5-1.8-6.9-1.8z",
        fill: primaryColor
      }),
      h('path', {
        d: "M550.5 76.4L230.9 270.6l240 130.5 322.2-187.8z",
        fill: secondaryColor
      }),
      h('path', {
        d: "M470.9 916V401.1",
        fill: secondaryColor
      }),
      h('path', {
        d: "M470.9 923.1c-3.9 0-7-3.1-7-7v-515c0-3.9 3.1-7 7-7s7 3.1 7 7V916c0 3.9-3.1 7.1-7 7.1z",
        fill: primaryColor
      }),
      h('path', {
        d: "M754.5 235.8L470.9 401.1",
        fill: secondaryColor
      }),
      h('path', {
        d: "M470.9 408.1c-2.4 0-4.8-1.2-6.1-3.5-1.9-3.3-0.8-7.6 2.5-9.6L751 229.7c3.4-2 7.6-0.8 9.6 2.5 1.9 3.3 0.8 7.6-2.5 9.6L474.5 407.2c-1.1 0.6-2.4 0.9-3.6 0.9z",
        fill: primaryColor
      }),
      h('path', {
        d: "M261.5 287.2l209.4 113.9",
        fill: secondaryColor
      }),
      h('path', {
        d: "M470.9 408.1c-1.1 0-2.3-0.3-3.3-0.8L258.1 293.4c-3.4-1.8-4.7-6.1-2.8-9.5 1.9-3.4 6.1-4.6 9.5-2.8L474.3 395c3.4 1.8 4.7 6.1 2.8 9.5-1.3 2.3-3.7 3.6-6.2 3.6z",
        fill: primaryColor
      }),
      h('path', {
        d: "M258.2 744.4l177.2 99.3",
        fill: secondaryColor
      }),
      h('path', {
        d: "M435.4 850.7c-1.2 0-2.3-0.3-3.4-0.9l-177.1-99.3c-3.4-1.9-4.6-6.2-2.7-9.5 1.9-3.4 6.1-4.6 9.5-2.7l177.1 99.3c3.4 1.9 4.6 6.2 2.7 9.5-1.3 2.3-3.7 3.6-6.1 3.6z",
        fill: primaryColor
      }),
      h('path', {
        d: "M258.2 694.8l177.2 99.3",
        fill: secondaryColor
      }),
      h('path', {
        d: "M435.4 801.1c-1.2 0-2.3-0.3-3.4-0.9l-177.1-99.3c-3.4-1.9-4.6-6.2-2.7-9.5 1.9-3.4 6.1-4.6 9.5-2.7L438.8 788c3.4 1.9 4.6 6.2 2.7 9.5-1.3 2.3-3.7 3.6-6.1 3.6z",
        fill: primaryColor
      }),
      h('path', {
        d: "M258.2 645.1l177.2 99.3",
        fill: secondaryColor
      }),
      h('path', {
        d: "M435.4 751.4c-1.2 0-2.3-0.3-3.4-0.9l-177.1-99.3c-3.4-1.9-4.6-6.2-2.7-9.5 1.9-3.4 6.1-4.6 9.5-2.7l177.1 99.3c3.4 1.9 4.6 6.2 2.7 9.5-1.3 2.3-3.7 3.6-6.1 3.6z",
        fill: primaryColor
      }),
      h('path', {
        d: "M222.7 538.9l248.2 135.5",
        fill: secondaryColor
      }),
      h('path', {
        d: "M219.335 545.028l6.708-12.289 248.241 135.49-6.707 12.289z",
        fill: primaryColor
      }),
      h('path', {
        d: "M393 430.7l40.3 20.1",
        fill: secondaryColor
      }),
      h('path', {
        d: "M433.3 457.8c-1.1 0-2.1-0.2-3.1-0.7L389.9 437c-3.5-1.7-4.9-5.9-3.1-9.4 1.7-3.5 6-4.9 9.4-3.1l40.3 20.1c3.5 1.7 4.9 5.9 3.1 9.4-1.3 2.4-3.8 3.8-6.3 3.8z",
        fill: primaryColor
      })
    ];
  }
}

class ServerNodeModel extends BaseCustomNodeModel { }

const ServerNodeConfig = {
  type: 'server',
  view: ServerNode,
  model: ServerNodeModel,
};

export default ServerNodeConfig;