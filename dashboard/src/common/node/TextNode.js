import { RectNode, RectNodeModel, h } from '@logicflow/core'

class TextLabelNode extends RectNode {
  getShape() {
    const { model } = this.props
    const { x, y, width = 10, height = 10 } = model
    const text = model.text?.value || '文本'
    const textStyle = model.getTextStyle()
    const halfW = width / 2
    const halfH = height / 2
    return h('g', {}, [
      h('rect', {
        x: x - halfW,
        y: y - halfH,
        width,
        height,
        fill: 'transparent',
        stroke: 'transparent'
      }),
      h('text', {
        x,
        y,
        textAnchor: 'middle',
        dominantBaseline: 'middle',
        fontSize: textStyle.fontSize || 14,
        fill: textStyle.fill || '#333'
      }, text)
    ])
  }

  getText() {
    return null
  }
}

class TextLabelNodeModel extends RectNodeModel {
  setAttributes() {
    const props = this.properties || {}
    this.width = props.width || 10
    this.height = props.height || 10
    this.resizable = false
    this.radius = 0
  }

  getDefaultAnchor() {
    return []
  }

  getTextStyle() {
    const style = super.getTextStyle()
    const props = this.properties || {}
    return { ...style, fontSize: props.textStyle?.fontSize || 14, fill: props.textStyle?.fill || '#333' }
  }
}

export default {
  type: 'textLabel',
  view: TextLabelNode,
  model: TextLabelNodeModel
}
