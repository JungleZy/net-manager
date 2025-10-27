import { LineEdge, LineEdgeModel, h } from '@logicflow/core'

/**
 * 带动画的边视图类
 * 当边的 properties.hasData 为 true 时，显示流动的小球动画
 */
class AnimatedEdgeView extends LineEdge {
  /**
     * 使用h函数创建SVG元素
     */
  getShape() {
    const { model } = this.props;
    const { startPoint, endPoint } = model;
    const pointsList = model.pointsList || model.points || [];

    // 获取基础路径
    const baseShape = super.getShape();

    // 组装运动路径：优先使用实际边的 pointsList，保证小球在真实路径上
    const buildPathD = (points) => {
      const pts = points && points.length > 1 ? points : [startPoint, endPoint];
      let d = `M ${pts[0].x} ${pts[0].y}`;
      for (let i = 1; i < pts.length; i++) {
        d += ` L ${pts[i].x} ${pts[i].y}`;
      }
      return d;
    };

    const pathD = buildPathD(pointsList);
    const reversePathD =
      pointsList && pointsList.length > 1
        ? buildPathD([...pointsList].slice().reverse())
        : `M ${endPoint.x} ${endPoint.y} L ${startPoint.x} ${startPoint.y}`;
    // 动画控制与性能优化参数（移除速率阈值过滤，增加视窗裁剪）
    const hasData = !!(model?.isAnimation || model?.properties?.hasData);
    const duration = model?.properties?.animationDuration || '2s';
    const graphEdgesCount = model?.graphModel?.edges?.length || 0;
    const denseMode = graphEdgesCount >= (model?.properties?.denseThreshold ?? 200);
    const maxAnimatedEdges = model?.properties?.maxAnimatedEdges ?? 120; // 最大同时小球动画的边数
    const idStr = String(model?.id || '');
    const idHash = idStr.split('').reduce((acc, ch) => acc + ch.charCodeAt(0), 0);
    const allowSlot = !denseMode || (graphEdgesCount > 0 && (idHash % graphEdgesCount) < maxAnimatedEdges);

    // 视窗裁剪：仅在可视区域内显示动画
    const gm = model?.graphModel || {};
    const tm = gm.transformModel || gm.transform || {};
    const SCALE_X = tm.SCALE_X ?? tm.scaleX ?? 1;
    const SCALE_Y = tm.SCALE_Y ?? tm.scaleY ?? 1;
    const TRANSLATE_X = tm.TRANSLATE_X ?? tm.translateX ?? 0;
    const TRANSLATE_Y = tm.TRANSLATE_Y ?? tm.translateY ?? 0;
    const canvasWidth = gm.width ?? 0;
    const canvasHeight = gm.height ?? 0;

    const ptsForView = (pointsList && pointsList.length > 0) ? pointsList : [startPoint, endPoint];
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    for (let i = 0; i < ptsForView.length; i++) {
      const p = ptsForView[i];
      const sx = p.x * SCALE_X + TRANSLATE_X;
      const sy = p.y * SCALE_Y + TRANSLATE_Y;
      if (sx < minX) minX = sx;
      if (sx > maxX) maxX = sx;
      if (sy < minY) minY = sy;
      if (sy > maxY) maxY = sy;
    }
    const intersectsViewport = (
      canvasWidth > 0 && canvasHeight > 0
        ? (maxX >= 0 && minX <= canvasWidth && maxY >= 0 && minY <= canvasHeight)
        : true
    );

    // 是否展示上传/下载小球（不再使用速率阈值）
    const showUpload = hasData && allowSlot && intersectsViewport;
    const showDownload = hasData && allowSlot && intersectsViewport;
    const showUploadFallback = false;
    const showDownloadFallback = false;
    const edgeId = model?.id || `animated-edge-${Date.now()}`;

    // 返回包含基础路径和小球的组
    return h('g', {}, [
      baseShape,
      // 隐藏的运动路径，供 mpath 绑定使用
      h('path', {
        id: `edge-motion-${edgeId}`,
        d: pathD,
        fill: 'none',
        stroke: 'none'
      }),
      h('path', {
        id: `edge-motion-reverse-${edgeId}`,
        d: reversePathD,
        fill: 'none',
        stroke: 'none'
      }),
      // 上传小球（仅在需要显示时渲染）
      ...((showUpload || showUploadFallback) ? [
        h(
          'circle',
          {
            cx: 0,
            cy: 0,
            r: 4,
            fill: '#52c41a',
            class: 'edge-animation-ball upload-circle'
          },
          [
            h(
              'animateMotion',
              {
                dur: duration,
                repeatCount: 'indefinite',
                rotate: 'auto'
              },
              [
                h('mpath', {
                  href: `#edge-motion-${edgeId}`
                })
              ]
            )
          ]
        )
      ] : []),
      // 下载小球（仅在需要显示时渲染）
      ...((showDownload || showDownloadFallback) ? [
        h(
          'circle',
          {
            cx: 0,
            cy: 0,
            r: 4,
            fill: '#1890ff',
            class: 'edge-animation-ball download-circle'
          },
          [
            h(
              'animateMotion',
              {
                dur: duration,
                repeatCount: 'indefinite',
                rotate: 'auto'
              },
              [
                h('mpath', {
                  href: `#edge-motion-reverse-${edgeId}`
                })
              ]
            )
          ]
        )
      ] : [])
    ]);
  }
}

/**
 * 带动画的边模型类
 */
class AnimatedEdgeModel extends LineEdgeModel {
  // 设置边的默认样式
  getEdgeStyle() {
    const style = super.getEdgeStyle()
    const { properties } = this
    style.stroke = '#999'

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
    const style = this.getEdgeStyle()
    style.stroke = '#1890ff'
    style.strokeWidth = 2
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
