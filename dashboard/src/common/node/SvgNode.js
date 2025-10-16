import { RectNode, RectNodeModel, h } from '@logicflow/core';
import insertCss from 'insert-css';

// 冻结默认样式配置
const DEFAULT_STYLES = Object.freeze({
  CIRCLE_FILL: 'white',
  PATH_FILL_DEFAULT: 'red'
});

class CustomIconNode extends RectNode {
  getCustomIcon = () => {
    const { model } = this.props;
    const { x, y, width, height } = model;
    const style = model.getNodeStyle();

    // 优化：预计算偏移量
    const halfWidth = width / 2;
    const halfHeight = height / 2;

    return h(
      'svg',
      {
        x: x - halfWidth,
        y: y - halfHeight,
        width,
        height,
        viewBox: `0 0 ${width} ${height}`,
      },
      [
        h('circle', {
          cx: '50%',
          cy: '50%',
          r: '50%',
          fill: DEFAULT_STYLES.CIRCLE_FILL,
        }),
        h('path', {
          d: 'M 39.7599939046071 14.139130434782608 C 42.99207598923147 5.808695652173912 50.36826332097323 0 58.944481129679474 0 C 70.49677452125768 0 78.83298623457102 10.74782608695652 79.87301264794026 23.54782608695652 C 79.87301264794026 23.54782608695652 80.43302687052369 26.730434782608697 79.20099558084013 32.45217391304348 C 77.5049525067303 40.243478260869566 73.5208513232082 47.18260869565217 68.16071519276679 52.469565217391306 L 39.7599939046071 80 L 11.839284807233199 52.452173913043474 C 6.47914867679179 47.18260869565217 2.49504749326967 40.243478260869566 0.7990044191598517 32.45217391304348 C -0.43302687052369576 26.730434782608697 0.12698735205973488 23.54782608695652 0.12698735205973488 23.54782608695652 C 1.167013765428963 10.74782608695652 9.503225478742316 0 21.055518870320512 0 C 29.631736679026766 0 36.52791181998273 5.808695652173912 39.7599939046071 14.139130434782608 Z',
          fill: style.fill,
          stroke: style.stroke,
        }),
      ],
    );
  };

  getShape = () => {
    const { model } = this.props;
    const { x, y, width, height, radius } = model;
    const style = model.getNodeStyle();

    // 优化：预计算偏移量
    const halfWidth = width / 2;
    const halfHeight = height / 2;

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
      this.getCustomIcon(),
    ]);
  };

  getText() {
    return null;
  }
}

class CustomIconNodeModel extends RectNodeModel {
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

  getTextStyle() {
    const { refX = 0, refY = 0, textStyle } = this.properties;
    const style = super.getTextStyle();

    // 优化：避免 JSON.parse/stringify
    return {
      ...style,
      fill: DEFAULT_STYLES.PATH_FILL_DEFAULT,
      ...textStyle,
      transform: `matrix(1 0 0 1 ${refX} ${refY})`,
    };
  }

  getNodeStyle() {
    const style = super.getNodeStyle();
    const { style: customNodeStyle } = this.properties;

    // 优化：避免 JSON.parse/stringify
    return {
      ...style,
      ...customNodeStyle
    };
  }
}

const SvgNode = {
  type: 'SvgNode',
  view: CustomIconNode,
  model: CustomIconNodeModel,
};

export default SvgNode;
insertCss(`
  #graph{
    width: 100%;
    height: 100%;
  }
  `);