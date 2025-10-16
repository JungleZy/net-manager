
import { GroupNode, GroupNodeModel } from '@logicflow/extension';

class CustomGroup extends GroupNode { }
class CustomGroupModel extends GroupNodeModel {
  initNodeData(data) {
    console.log("initNodeData", data);

    super.initNodeData(data);

    // 在调用 super 之前设置 isRestrict，确保它能被正确初始化
    if (data.properties && data.properties.isRestrict !== undefined) {
      this.isRestrict = data.properties.isRestrict;
    }
    // 设置其他属性
    this.resizable = true;
    this.width = 480;
    this.height = 280;
    this.radius = data.properties?.borderRadius;
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
}

export default {
  type: 'customGroup',
  view: CustomGroup,
  model: CustomGroupModel,
};