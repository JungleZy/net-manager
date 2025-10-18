import { h } from 'vue'
import { LineEdge, LineEdgeModel } from '@logicflow/core'

/**
 * 带动画的边视图类
 * 当边的 properties.hasData 为 true 时，显示流动的小球动画
 */
class AnimatedEdgeView extends LineEdge {

}

/**
 * 带动画的边模型类
 */
class AnimatedEdgeModel extends LineEdgeModel {
  // 设置边的默认样式
  getEdgeStyle() {
    const style = super.getEdgeStyle()
    const { properties } = this

    if (properties?.hasData) {
      return {
        ...style,
        stroke: '#1890ff',
        strokeWidth: 3
      }
    }

    return style
  }
  setAttributes() {
    this.isAnimation = false
  }

  getEdgeAnimationStyle() {
    const style = super.getEdgeAnimationStyle()
    style.strokeDasharray = '5 5'
    style.stroke = '#1677FF'
    style.animationDuration = '60s'
    return style
  }
}

/**
 * 导出边配置对象
 */
export default {
  type: 'animated-line',
  view: AnimatedEdgeView,
  model: AnimatedEdgeModel
}
