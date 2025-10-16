
import { GroupNode, GroupNodeModel } from '@logicflow/extension';
import { h } from '@logicflow/core';

// 冻结常量配置，避免运行时修改和重复创建
const DEFAULTS = Object.freeze({
  MIN_PADDING: 20,        // 分组边界与内部节点的最小间距
  MIN_SIZE: 100,          // 无子节点时的最小尺寸
  BORDER_RADIUS: 8,       // 默认圆角
  TEXT_OFFSET_X: 6,       // 文本X轴偏移
  TEXT_OFFSET_Y: -10,     // 文本Y轴偏移
  TEXT_FONT_SIZE: 13,     // 文本字体大小
  FILL_COLOR: '#F4F5F6',  // 默认填充色
  FILL_OPACITY: 0.3,      // 默认填充透明度
  STROKE_COLOR: '#CECECE', // 默认边框色
  STROKE_WIDTH: 2,        // 默认边框宽度
});

class CustomGroup extends GroupNode {

}
class CustomGroupModel extends GroupNodeModel {
  constructor(...args) {
    super(...args);
    // 缓存子节点边界，避免频繁重新计算
    this._childrenBoundsCache = null;
    this._lastChildrenHash = null;
  }

  initNodeData(data) {
    // 优化：一次性处理 properties 中的尺寸数据
    const props = data.properties;
    if (props) {
      if (props.width !== undefined) {
        data.width = props.width;
        delete props.width;
      }
      if (props.height !== undefined) {
        data.height = props.height;
        delete props.height;
      }
    }

    super.initNodeData(data);

    // 优化：直接访问属性，减少条件判断
    if (props?.isRestrict !== undefined) {
      this.isRestrict = props.isRestrict;
    }

    // 如果传入了 width 和 height（在根节点），在 super 之后重新应用
    this.width = data.width;
    this.height = data.height;
    this.radius = props?.borderRadius || DEFAULTS.BORDER_RADIUS;
    this.resizable = true;
  }

  getNodeStyle() {
    const style = super.getNodeStyle();
    const props = this.properties;

    // 优化：直接赋值，避免展开操作符的性能开销
    style.fill = props.fillColor || DEFAULTS.FILL_COLOR;
    style.fillOpacity = props.fillOpacity !== undefined ? props.fillOpacity : DEFAULTS.FILL_OPACITY;
    style.stroke = props.strokeColor || DEFAULTS.STROKE_COLOR;
    style.strokeWidth = props.strokeWidth !== undefined ? props.strokeWidth : DEFAULTS.STROKE_WIDTH;
    style.strokeDasharray = props.strokeDasharray || '';

    return style;
  }

  // 监听节点属性变化，当 width 或 height 变化时重新计算文本位置
  setAttributes() {
    super.setAttributes();
    // 清除缓存，因为节点属性已变化
    this._invalidateCache();
    // resize 后重新计算文本位置
    this.updateTextPosition();
  }

  // 使缓存失效
  _invalidateCache() {
    this._childrenBoundsCache = null;
    this._lastChildrenHash = null;
  }

  // 计算子节点的哈希值，用于判断子节点是否变化
  _getChildrenHash() {
    const children = this.children || [];
    if (children.length === 0) return '';

    // 简单的哈希：子节点ID拼接
    return children.join(',');
  }

  // 获取子节点边界（带缓存）
  _getChildrenBounds() {
    const children = this.children || [];
    const childrenHash = this._getChildrenHash();

    // 如果子节点没有变化，返回缓存
    if (childrenHash === this._lastChildrenHash && this._childrenBoundsCache) {
      return this._childrenBoundsCache;
    }

    if (children.length === 0) {
      return null;
    }

    // 计算边界
    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;

    for (let i = 0, len = children.length; i < len; i++) {
      const childNode = this.graphModel.getNodeModelById(children[i]);
      if (!childNode) continue;

      const childWidth = childNode.width || 60;
      const childHeight = childNode.height || 60;
      const childLeft = childNode.x - childWidth / 2;
      const childRight = childNode.x + childWidth / 2;
      const childTop = childNode.y - childHeight / 2;
      const childBottom = childNode.y + childHeight / 2;

      if (childLeft < minX) minX = childLeft;
      if (childTop < minY) minY = childTop;
      if (childRight > maxX) maxX = childRight;
      if (childBottom > maxY) maxY = childBottom;
    }

    const bounds = {
      minX,
      minY,
      maxX,
      maxY,
      width: maxX - minX + DEFAULTS.MIN_PADDING * 2,
      height: maxY - minY + DEFAULTS.MIN_PADDING * 2,
    };

    // 缓存结果
    this._childrenBoundsCache = bounds;
    this._lastChildrenHash = childrenHash;

    return bounds;
  }

  // 重写 getResizeShape 方法，在 resize 过程中限制最小尺寸
  getResizeShape(deltaX, deltaY, resizeControl) {
    // 先获取默认的 resize 结果
    const shape = super.getResizeShape(deltaX, deltaY, resizeControl);

    // 注意：resize 过程中不使用缓存，因为子节点位置可能实时变化
    // 但我们优化了计算逻辑
    const children = this.children || [];

    if (children.length === 0) {
      // 如果没有子节点，设置最小尺寸
      if (shape.width < DEFAULTS.MIN_SIZE) shape.width = DEFAULTS.MIN_SIZE;
      if (shape.height < DEFAULTS.MIN_SIZE) shape.height = DEFAULTS.MIN_SIZE;
      return shape;
    }

    // 使用缓存的边界计算（如果可用）
    const bounds = this._getChildrenBounds();
    if (bounds) {
      // 限制最小尺寸
      if (shape.width < bounds.width) {
        shape.width = bounds.width;
      }
      if (shape.height < bounds.height) {
        shape.height = bounds.height;
      }
    }

    return shape;
  }

  // 更新文本位置：将文本放在分组左上角
  updateTextPosition() {
    const text = this.text;
    if (text && typeof text === 'object') {
      // 优化：减少重复计算，直接赋值
      const halfWidth = this.width / 2;
      const halfHeight = this.height / 2;
      text.x = this.x - halfWidth + DEFAULTS.TEXT_OFFSET_X;
      text.y = this.y - halfHeight + DEFAULTS.TEXT_OFFSET_Y;
    }
  }

  // 获取文本样式：标签样式，背景色根据边框颜色，文字颜色自动对比
  getTextStyle() {
    const style = super.getTextStyle();
    const strokeColor = this.properties?.strokeColor || DEFAULTS.STROKE_COLOR;

    // 优化：直接赋值，避免展开操作符
    style.fontSize = DEFAULTS.TEXT_FONT_SIZE;
    style.color = strokeColor;
    style.textAnchor = 'start';
    style.overflowMode = 'default';

    return style;
  }
}

export default {
  type: 'customGroup',
  view: CustomGroup,
  model: CustomGroupModel,
};