import { h } from '@logicflow/core';
import { RectResizeModel, RectResizeView } from '@logicflow/extension';

const defaultWidth = 500;
const defaultHeight = 300;
const DEFAULT_BOTTOM_Z_INDEX = -10000;

/**
 * 自定义分组节点模型
 * 支持所有 GroupNode 原有功能，并新增填充色和透明度设置
 */
export class CustomGroupNodeModel extends RectResizeModel {
  isGroup = true;

  initNodeData(data) {
    super.initNodeData(data);
    let children = [];
    if (Array.isArray(data.children)) {
      children = data.children;
    }
    // 初始化组的子节点
    this.children = new Set(children);
    this.width = defaultWidth;
    this.height = defaultHeight;
    this.foldedWidth = 80;
    this.foldedHeight = 60;
    this.zIndex = DEFAULT_BOTTOM_Z_INDEX;
    this.radius = 0;

    this.text.editable = false;
    this.text.draggable = false;

    this.isRestrict = false;
    this.resizable = false;
    this.autoToFront = false;
    this.foldable = false;

    // 初始化折叠状态
    if (this.properties.isFolded === undefined) {
      this.properties.isFolded = false;
    }
    this.isFolded = !!this.properties.isFolded;

    // 初始化填充色和透明度
    if (this.properties.fillColor === undefined) {
      this.properties.fillColor = '#F4F5F6'; // 默认填充色
    }
    if (this.properties.fillOpacity === undefined) {
      this.properties.fillOpacity = 0.3; // 默认透明度 (0-1)
    }
    if (this.properties.strokeColor === undefined) {
      this.properties.strokeColor = '#CECECE'; // 默认边框色
    }
    if (this.properties.strokeWidth === undefined) {
      this.properties.strokeWidth = 2; // 默认边框宽度
    }
    if (this.properties.strokeDasharray === undefined) {
      this.properties.strokeDasharray = ''; // 默认为实线，如'5,5'表示虚线
    }

    // 延迟折叠处理
    setTimeout(() => {
      this.isFolded && this.foldGroup(this.isFolded);
    });

    // 初始化折叠状态缓存
    this.unfoldedWidth = defaultWidth;
    this.unfoldedHeight = defaultHeight;
    this.childrenLastFoldStatus = {};
  }

  /**
   * 获取节点样式 - 应用填充色、透明度和边框样式
   */
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

  getResizeOutlineStyle() {
    const style = super.getResizeOutlineStyle();
    style.stroke = 'none';
    return style;
  }

  /**
   * 折叠分组
   * 1. 折叠分组的宽高
   * 2. 处理分组子节点
   * 3. 处理连线
   */
  foldGroup(isFolded) {
    if (isFolded === this.isFolded) {
      return;
    }
    this.setProperty('isFolded', isFolded);
    this.isFolded = isFolded;

    // step 1: 调整尺寸
    if (isFolded) {
      this.x = this.x - this.width / 2 + this.foldedWidth / 2;
      this.y = this.y - this.height / 2 + this.foldedHeight / 2;
      this.unfoldedWidth = this.width;
      this.unfoldedHeight = this.height;
      this.width = this.foldedWidth;
      this.height = this.foldedHeight;
    } else {
      this.width = this.unfoldedWidth;
      this.height = this.unfoldedHeight;
      this.x = this.x + this.width / 2 - this.foldedWidth / 2;
      this.y = this.y + this.height / 2 - this.foldedHeight / 2;
    }

    // step 2: 处理子节点
    let allEdges = [...this.incoming.edges, ...this.outgoing.edges];
    this.children.forEach((elementId) => {
      const nodeModel = this.graphModel.getElement(elementId);
      if (nodeModel) {
        const foldStatus = nodeModel.isFolded;

        if (nodeModel.isGroup && !nodeModel.isFolded) {
          nodeModel.foldGroup(isFolded);
        }

        if (nodeModel.isGroup && !isFolded) {
          const lastFoldStatus = this.childrenLastFoldStatus[elementId];
          if (lastFoldStatus !== undefined && lastFoldStatus !== nodeModel.isFolded) {
            nodeModel.foldGroup(lastFoldStatus);
          }
        }

        this.childrenLastFoldStatus[elementId] = !!foldStatus;
        nodeModel.visible = !isFolded;

        const incomingEdges = nodeModel.incoming.edges;
        const outgoingEdges = nodeModel.outgoing.edges;
        allEdges = [...allEdges, ...incomingEdges, ...outgoingEdges];
      }
    });

    // step 3: 处理连线
    this.foldEdge(isFolded, allEdges);
  }

  getAnchorStyle(anchorInfo) {
    const style = super.getAnchorStyle(anchorInfo);
    style.stroke = 'transparent';
    style.fill = 'transparent';
    if (style.hover) {
      style.hover.fill = 'transparent';
      style.hover.stroke = 'transparent';
    }
    return style;
  }

  /**
   * 折叠分组的时候，处理分组自身的连线和分组内部子节点上的连线
   */
  foldEdge(isFolded, allEdges) {
    allEdges.forEach((edgeModel, index) => {
      const { id, sourceNodeId, targetNodeId, startPoint, endPoint, type, text } = edgeModel;
      const properties = edgeModel.getProperties();
      const data = {
        id: `${id}__${index}`,
        sourceNodeId,
        targetNodeId,
        startPoint,
        endPoint,
        type,
        properties,
        text: text?.value,
      };

      if (edgeModel.virtual) {
        this.graphModel.deleteEdgeById(edgeModel.id);
      }

      let targetNodeIdGroup = this.graphModel.group.getNodeGroup(targetNodeId);
      if (!targetNodeIdGroup) {
        targetNodeIdGroup = this.graphModel.getNodeModelById(targetNodeId);
      }

      let sourceNodeIdGroup = this.graphModel.group.getNodeGroup(sourceNodeId);
      if (!sourceNodeIdGroup) {
        sourceNodeIdGroup = this.graphModel.getNodeModelById(sourceNodeId);
      }

      // 折叠时，处理未被隐藏的边的逻辑
      if (isFolded && edgeModel.visible !== false) {
        if (this.children.has(sourceNodeId) || this.id === sourceNodeId) {
          data.startPoint = undefined;
          data.sourceNodeId = this.id;
        } else {
          data.endPoint = undefined;
          data.targetNodeId = this.id;
        }

        if (targetNodeIdGroup.id !== this.id || sourceNodeIdGroup.id !== this.id) {
          this.createVirtualEdge(data);
        }
        edgeModel.visible = false;
      }

      // 展开时，处理被隐藏的边的逻辑
      if (!isFolded && edgeModel.visible === false) {
        if (targetNodeIdGroup && targetNodeIdGroup.isGroup && targetNodeIdGroup.isFolded) {
          data.targetNodeId = targetNodeIdGroup.id;
          data.endPoint = undefined;
          this.createVirtualEdge(data);
        } else if (sourceNodeIdGroup && sourceNodeIdGroup.isGroup && sourceNodeIdGroup.isFolded) {
          data.sourceNodeId = sourceNodeIdGroup.id;
          data.startPoint = undefined;
          this.createVirtualEdge(data);
        } else {
          edgeModel.visible = true;
        }
      }
    });
  }

  createVirtualEdge(edgeData) {
    edgeData.pointsList = undefined;
    const model = this.graphModel.addEdge(edgeData);
    model.virtual = true;
    model.text.editable = false;
    model.isFoldedEdge = true;
  }

  isInRange({ minX, minY, maxX, maxY }) {
    return (
      minX >= this.x - this.width / 2 &&
      maxX <= this.x + this.width / 2 &&
      minY >= this.y - this.height / 2 &&
      maxY <= this.y + this.height / 2
    );
  }

  isAllowMoveTo({ minX, minY, maxX, maxY }) {
    return {
      x: minX >= this.x - this.width / 2 && maxX <= this.x + this.width / 2,
      y: minY >= this.y - this.height / 2 && maxY <= this.y + this.height / 2,
    };
  }

  setAllowAppendChild(isAllow) {
    this.setProperty('groupAddable', isAllow);
  }

  /**
   * 添加分组子节点
   */
  addChild(id) {
    this.children.add(id);
    this.graphModel.eventCenter.emit('group:add-node', { data: this.getData() });
  }

  /**
   * 删除分组子节点
   */
  removeChild(id) {
    this.children.delete(id);
    this.graphModel.eventCenter.emit('group:remove-node', { data: this.getData() });
  }

  getAddableOutlineStyle() {
    return {
      stroke: '#FEB663',
      strokeWidth: 2,
      strokeDasharray: '4 4',
      fill: 'transparent',
    };
  }

  getData() {
    const data = super.getData();
    data.children = [];
    this.children.forEach((childId) => {
      const model = this.graphModel.getNodeModelById(childId);
      if (model && !model.virtual) {
        data.children.push(childId);
      }
    });
    const { properties } = data;
    delete properties?.groupAddable;
    delete properties?.isFolded;
    return data;
  }

  getHistoryData() {
    const data = super.getData();
    data.children = [...this.children];
    data.isGroup = true;
    const { properties } = data;
    delete properties?.groupAddable;
    if (properties?.isFolded) {
      data.x = data.x + this.unfoldedWidth / 2 - this.foldedWidth / 2;
      data.y = data.y + this.unfoldedHeight / 2 - this.foldedHeight / 2;
    }
    return data;
  }

  /**
   * 是否允许此节点添加到此分组中
   */
  isAllowAppendIn(nodeData) {
    return true;
  }

  /**
   * 当groupA被添加到groupB中时，将groupB及groupB所属的group的zIndex减1
   */
  toBack() {
    this.zIndex--;
  }

  /**
   * 设置填充色
   */
  setFillColor(color) {
    this.setProperty('fillColor', color);
  }

  /**
   * 设置透明度
   */
  setFillOpacity(opacity) {
    this.setProperty('fillOpacity', opacity);
  }

  /**
   * 设置边框颜色
   */
  setStrokeColor(color) {
    this.setProperty('strokeColor', color);
  }

  /**
   * 设置边框宽度
   */
  setStrokeWidth(width) {
    this.setProperty('strokeWidth', width);
  }

  /**
   * 设置边框样式（实线/虚线）
   */
  setStrokeDasharray(dasharray) {
    this.setProperty('strokeDasharray', dasharray);
  }
}

/**
 * 自定义分组节点视图
 */
export class CustomGroupNode extends RectResizeView {
  getControlGroup() {
    const { resizable, properties } = this.props.model;
    return resizable && !properties.isFolded ? super.getControlGroup() : null;
  }

  getAddableShape() {
    const { width, height, x, y, radius, properties, getAddableOutlineStyle } = this.props.model;
    if (!properties.groupAddable) return null;

    const { strokeWidth = 0 } = this.props.model.getNodeStyle();
    const style = getAddableOutlineStyle();
    const newWidth = width + strokeWidth + 8;
    const newHeight = height + strokeWidth + 8;

    return h('rect', {
      ...style,
      width: newWidth,
      height: newHeight,
      x: x - newWidth / 2,
      y: y - newHeight / 2,
      rx: radius,
      ry: radius,
    });
  }

  getFoldIcon() {
    const { model } = this.props;
    const foldX = model.x - model.width / 2 + 5;
    const foldY = model.y - model.height / 2 + 5;

    if (!model.foldable) return null;

    const iconIcon = h('path', {
      fill: 'none',
      stroke: '#818281',
      strokeWidth: 2,
      'pointer-events': 'none',
      d: model.properties.isFolded
        ? `M ${foldX + 3},${foldY + 6} ${foldX + 11},${foldY + 6} M${foldX + 7},${foldY + 2} ${foldX + 7},${foldY + 10}`
        : `M ${foldX + 3},${foldY + 6} ${foldX + 11},${foldY + 6} `,
    });

    return h('g', {}, [
      h('rect', {
        height: 12,
        width: 14,
        rx: 2,
        ry: 2,
        strokeWidth: 1,
        fill: '#F4F5F6',
        stroke: '#CECECE',
        cursor: 'pointer',
        x: model.x - model.width / 2 + 5,
        y: model.y - model.height / 2 + 5,
        onClick: () => {
          model.foldGroup(!model.properties.isFolded);
        },
      }),
      iconIcon,
    ]);
  }

  getResizeShape() {
    return h('g', {}, [
      this.getAddableShape(),
      super.getResizeShape(),
      this.getFoldIcon(),
    ]);
  }
}

export default {
  type: 'customGroup',
  view: CustomGroupNode,
  model: CustomGroupNodeModel,
};
