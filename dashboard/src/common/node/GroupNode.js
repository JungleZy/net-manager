
import { GroupNode, GroupNodeModel } from '@logicflow/extension';
import { h } from '@logicflow/core';

class CustomGroup extends GroupNode {

}
class CustomGroupModel extends GroupNodeModel {
  initNodeData(data) {

    // 如果 properties 中存在 width 和 height，将其移到根节点并删除
    if (data.properties?.width !== undefined) {
      data.width = data.properties.width;
      delete data.properties.width;
    }
    if (data.properties?.height !== undefined) {
      data.height = data.properties.height;
      delete data.properties.height;
    }

    super.initNodeData(data);

    if (data.properties && data.properties.isRestrict !== undefined) {
      this.isRestrict = data.properties.isRestrict;
    }

    // 如果传入了 width 和 height（在根节点），在 super 之后重新应用
    // 因为父类可能重置为默认值
    if (data.width !== undefined) {
      this.width = data.width;
    }
    if (data.height !== undefined) {
      this.height = data.height;
    }
    this.radius = data.properties?.borderRadius || 8;
    // 设置其他属性
    this.resizable = true;
  }

  getNodeStyle() {
    const style = super.getNodeStyle();
    const { fillColor, fillOpacity, strokeColor, strokeWidth, strokeDasharray } = this.properties;

    return {
      ...style,
      fill: fillColor || '#F4F5F6',
      fillOpacity: fillOpacity !== undefined ? fillOpacity : 0.3,
      stroke: strokeColor || '#CECECE',
      strokeWidth: strokeWidth !== undefined ? strokeWidth : 2,
      strokeDasharray: strokeDasharray || '', // 支持虚线样式
    };
  }

  // 监听节点属性变化，当 width 或 height 变化时重新计算文本位置
  setAttributes() {
    super.setAttributes();
    // resize 后重新计算文本位置
    this.updateTextPosition();
  }

  // 更新文本位置：将文本放在分组左上角
  updateTextPosition() {
    if (this.text && typeof this.text === 'object') {
      // 计算分组的左上角位置
      const leftX = this.x - this.width / 2;
      const topY = this.y - this.height / 2;
      // 将文本放在左上角，稍微向内偏移
      this.text.x = leftX + 6;
      this.text.y = topY + 10;
    }
  }

  // 获取文本样式：标签样式，背景色根据边框颜色，文字颜色自动对比
  getTextStyle() {
    const style = super.getTextStyle();
    const node = super.getProperties();
    console.log(node);
    const strokeColor = node?.strokeColor || '#CECECE';
    return {
      ...style,
      fontSize: 13,
      color: strokeColor,              // 文字颜色
      textAnchor: 'start',           // 左对齐
      overflowMode: 'default',       // 不自动换行
    };
  }
}

export default {
  type: 'customGroup',
  view: CustomGroup,
  model: CustomGroupModel,
};