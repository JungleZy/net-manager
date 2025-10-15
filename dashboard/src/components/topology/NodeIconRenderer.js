/**
 * 节点图标渲染器
 * 负责将不同类型的设备渲染为 SVG 图标
 * 使用 assets/svg 中的官方 SVG 文件
 */

// 导入 SVG 文件
import TopologyPCSvg from '@/assets/svg/TopologyPC.svg?raw'
import TopologyLaptopSvg from '@/assets/svg/TopologyLaptop.svg?raw'
import TopologyServerSvg from '@/assets/svg/TopologyServer.svg?raw'
import TopologyRouterSvg from '@/assets/svg/TopologyRouter.svg?raw'
import TopologySwitchesSvg from '@/assets/svg/TopologySwitches.svg?raw'
import TopologyFireWallSvg from '@/assets/svg/TopologyFireWall.svg?raw'
import TopologyPrinterSvg from '@/assets/svg/TopologyPrinter.svg?raw'

export class NodeIconRenderer {
  /**
   * 渲染节点图标
   * @param {d3.Selection} nodeGroup - D3选择的节点组
   * @param {Object} nodeData - 节点数据
   * @param {number} size - 图标大小
   */
  static renderIcon(nodeGroup, nodeData, size = 60) {
    const type = nodeData.type || 'pc'
    const status = nodeData.status || 'online'

    // 清空之前的图标
    nodeGroup.selectAll('.node-icon-svg').remove()

    // 创建图标容器
    const iconGroup = nodeGroup
      .append('g')
      .attr('class', 'node-icon-svg')
      .attr('transform', `translate(${-size / 2}, ${-size / 2})`)

    // 根据类型选择 SVG
    let svgContent = ''
    switch (type) {
      case 'pc':
        svgContent = TopologyPCSvg
        break
      case 'laptop':
        svgContent = TopologyLaptopSvg
        break
      case 'server':
        svgContent = TopologyServerSvg
        break
      case 'router':
        svgContent = TopologyRouterSvg
        break
      case 'switch':
        svgContent = TopologySwitchesSvg
        break
      case 'firewall':
        svgContent = TopologyFireWallSvg
        break
      case 'printer':
        svgContent = TopologyPrinterSvg
        break
      default:
        // 默认图标
        this.renderDefaultIcon(iconGroup, size)
        return
    }

    // 解析 SVG 并提取 viewBox 和 path
    const parser = new DOMParser()
    const svgDoc = parser.parseFromString(svgContent, 'image/svg+xml')
    const svgElement = svgDoc.querySelector('svg')

    if (!svgElement) {
      this.renderDefaultIcon(iconGroup, size)
      return
    }

    const viewBox = svgElement.getAttribute('viewBox') || '0 0 1024 1024'
    const paths = svgElement.querySelectorAll('path')

    // 创建 SVG 容器
    const svg = iconGroup
      .append('svg')
      .attr('width', size)
      .attr('height', size)
      .attr('viewBox', viewBox)

    // 添加所有 path 元素
    paths.forEach(path => {
      const d = path.getAttribute('d')
      const fill = path.getAttribute('fill')
      const pId = path.getAttribute('p-id')

      // 如果是离线状态，将颜色转为灰度
      let pathFill = fill
      if (status === 'offline') {
        pathFill = this.convertToGrayscale(fill)
      }

      svg.append('path')
        .attr('d', d)
        .attr('fill', pathFill)
        .attr('p-id', pId)
    })
  }

  /**
   * 将颜色转换为灰度
   */
  static convertToGrayscale(color) {
    if (!color || color === 'none' || color === 'transparent') {
      return color
    }

    // 已经是灰色系列，直接返回
    if (color.startsWith('#')) {
      const hex = color.substring(1)
      if (hex.length === 6) {
        const r = parseInt(hex.substring(0, 2), 16)
        const g = parseInt(hex.substring(2, 4), 16)
        const b = parseInt(hex.substring(4, 6), 16)

        // 计算灰度值
        const gray = Math.round(0.299 * r + 0.587 * g + 0.114 * b)
        const grayHex = gray.toString(16).padStart(2, '0')
        return `#${grayHex}${grayHex}${grayHex}`
      }
    }

    // 其他情况返回浅灰色
    return '#cccccc'
  }

  /**
   * 渲染默认图标
   */
  static renderDefaultIcon(g, size) {
    g.append('circle')
      .attr('cx', size / 2)
      .attr('cy', size / 2)
      .attr('r', size * 0.3)
      .attr('fill', '#1890ff')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)

    g.append('text')
      .attr('x', size / 2)
      .attr('y', size / 2)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('fill', '#fff')
      .attr('font-size', size * 0.3)
      .text('?')
  }

  /**
   * 文本自动换行处理
   * @param {d3.Selection} textElement - D3选择的text元素
   * @param {string} text - 要显示的文本
   * @param {number} maxWidth - 最大宽度（像素）
   */
  static wrapText(textElement, text, maxWidth = 60) {
    if (!text) return

    const words = text.split('')  // 按字符分割，支持中文
    const lineHeight = 14  // 行高（像素）
    let line = ''
    let lineNumber = 0
    const lines = []

    // 创建临时测量元素
    const testTspan = textElement
      .append('tspan')
      .style('visibility', 'hidden')

    // 按字符逐个检测宽度
    for (let i = 0; i < words.length; i++) {
      const testLine = line + words[i]
      testTspan.text(testLine)
      const testWidth = testTspan.node().getComputedTextLength()

      if (testWidth > maxWidth && line.length > 0) {
        // 超出宽度，换行
        lines.push(line)
        line = words[i]
      } else {
        line = testLine
      }
    }

    // 添加最后一行
    if (line) {
      lines.push(line)
    }

    // 移除测量元素
    testTspan.remove()

    // 清空原有内容
    textElement.text('')

    // 添加所有行，第一行从0开始，后续行逐行向下
    lines.forEach((lineText, i) => {
      textElement
        .append('tspan')
        .attr('x', 0)
        .attr('dy', i === 0 ? 0 : lineHeight)  // 第一行dy=0（由text元素的dy控制），后续行相对偏移
        .text(lineText)
    })
  }
}

export default NodeIconRenderer
