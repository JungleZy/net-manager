import { RectNode, RectNodeModel, h } from '@logicflow/core';
import insertCss from 'insert-css';
import { DEFAULT_STYLES } from './nodeConfig';

class BaseCustomNode extends RectNode {
  getCustomIcon = (svgContent) => {
    const { model } = this.props;
    const { x, y, width, height } = model;

    // 优化：预计算偏移量，减少重复计算
    const halfWidth = width / 2;
    const halfHeight = height / 2;

    return h(
      'svg',
      {
        x: x - halfWidth,
        y: y - halfHeight,
        width,
        height,
        viewBox: '0 0 1024 1024',
      },
      svgContent
    );
  };

  getShape = () => {
    const { model } = this.props;
    const { x, y, width, height, radius, text } = model;
    const style = model.getNodeStyle();

    // 优化：预计算偏移量
    const halfWidth = width / 2;
    const halfHeight = height / 2;

    // 创建title元素用于鼠标悬停时显示完整文本
    const titleElement = text?.value ? h('title', {}, text.value) : null;

    return h('g', {}, [
      h('rect', {
        ...style,
        stroke: 'transparent',
        fill: 'transparent',
        x: x - halfWidth,
        y: y - halfHeight,
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
    const { x, y, height, text } = model;

    // 如果没有文本，直接返回null
    if (!text?.value) {
      return null;
    }

    const displayText = text.value;
    const textStyle = model.getTextStyle();

    return h(
      'text',
      {
        x: x,
        y: y + height / 2 + 5, // 在节点下方显示文本
        textAnchor: 'middle',
        fontSize: textStyle.fontSize || DEFAULT_STYLES.DEFAULT_FONT_SIZE,
        fill: textStyle.fill || DEFAULT_STYLES.TEXT_FILL,
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
    const { textStyle } = this.properties;
    const style = super.getTextStyle();

    // 优化：避免 JSON.parse/stringify，直接展开
    return {
      ...style,
      fill: DEFAULT_STYLES.TEXT_FILL,
      ...textStyle
    };
  }

  getNodeStyle() {
    const style = super.getNodeStyle();
    const { style: customNodeStyle, status } = this.properties;

    // 优化：根据status设置节点颜色，使用常量
    const fillColor = status === 'offline'
      ? DEFAULT_STYLES.OFFLINE_COLOR
      : DEFAULT_STYLES.ONLINE_COLOR;

    return {
      ...style,
      fill: fillColor,
      ...customNodeStyle
    };
  }
}

export { BaseCustomNode, BaseCustomNodeModel };