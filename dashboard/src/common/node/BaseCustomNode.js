import { RectNode, RectNodeModel, h } from '@logicflow/core';
import insertCss from 'insert-css';

class BaseCustomNode extends RectNode {
  getCustomIcon = (svgContent) => {
    const { model } = this.props;
    const { x, y, width, height } = model;
    const style = model.getNodeStyle();

    return h(
      'svg',
      {
        x: x - width / 2,
        y: y - height / 2,
        width,
        height,
        viewBox: '0 0 1024 1024',
      },
      svgContent
    );
  };

  getShape = () => {
    const { model } = this.props;
    const { x, y, width, height, radius } = model;
    const style = model.getNodeStyle();
    const { text } = model;

    // 创建title元素用于鼠标悬停时显示完整文本
    const titleElement = text && text.value ? h('title', {}, text.value) : null;

    return h('g', {}, [
      h('rect', {
        ...style,
        stroke: 'transparent',
        fill: 'transparent',
        x: x - width / 2,
        y: y - height / 2,
        rx: radius,
        ry: radius,
        width,
        height,
      }),
      this.getCustomIcon(this.getSVGContent()),
      titleElement
    ]);
  };

  getText() {
    const { model } = this.props;
    const { x, y, width, height } = model;
    const { text } = model;

    // 如果没有文本，直接返回null
    if (!text || !text.value) {
      return null;
    }

    // 限制文本长度最多显示9个字
    let displayText = text.value;


    // 获取文本样式
    const textStyle = model.getTextStyle();

    return h(
      'text',
      {
        x: x,
        y: y + height / 2 + 5, // 在节点下方显示文本，距离节点底部10像素
        textAnchor: 'middle',
        fontSize: textStyle.fontSize || 12,
        fill: textStyle.fill || '#333',
        ...textStyle
      },
      displayText
    );
  }

  // 子类需要实现此方法，返回SVG路径内容
  getSVGContent() {
    return [];
  }
}

class BaseCustomNodeModel extends RectNodeModel {
  setAttributes() {
    const { width, height, radius } = this.properties;
    if (width) {
      this.width = width;
    }
    if (height) {
      this.height = height;
    }
    if (radius) {
      this.radius = radius;
    }
  }

  getDefaultAnchor() {
    // 返回一个中心锚点，让所有边都连接到节点中心
    return [
      {
        x: this.x,
        y: this.y,
        id: `${this.id}_center`
      }
    ];
  }

  getTextStyle() {
    const {
      textStyle,
    } = this.properties;
    const style = super.getTextStyle();

    return {
      ...style,
      fill: '#333',
      ...(textStyle ? JSON.parse(JSON.stringify(textStyle)) : {}),
    };
  }

  getNodeStyle() {
    const style = super.getNodeStyle();
    const {
      style: customNodeStyle,
      status,
    } = this.properties;

    // 根据status设置节点颜色
    let fillColor = '#0276F7'; // 默认在线状态颜色
    if (status === 'offline') {
      fillColor = 'red'; // 离线状态颜色
    }

    return {
      ...style,
      fill: fillColor,
      ...(customNodeStyle ? JSON.parse(JSON.stringify(customNodeStyle)) : {}),
    };
  }
}

export { BaseCustomNode, BaseCustomNodeModel };