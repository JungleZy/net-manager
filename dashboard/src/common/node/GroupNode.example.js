/**
 * CustomGroupNode 使用示例
 * 
 * 本文件包含 CustomGroupNode 的各种使用场景示例
 */

// ============================================
// 示例 1: 创建基本分组
// ============================================
export const createBasicGroup = (lf) => {
  lf.addNode({
    type: 'customGroup',
    x: 300,
    y: 200,
    properties: {
      width: 400,
      height: 300,
      fillColor: '#E3F2FD',      // 浅蓝色
      fillOpacity: 0.5,           // 50% 透明度
      strokeColor: '#2196F3',     // 蓝色边框
      strokeWidth: 2
    },
    text: {
      value: '基础分组',
      editable: true
    }
  });
};

// ============================================
// 示例 2: 创建不同主题的分组
// ============================================
export const createThemedGroups = (lf) => {
  // 蓝色主题 - 网络设备组
  lf.addNode({
    type: 'customGroup',
    x: 200,
    y: 200,
    properties: {
      width: 400,
      height: 300,
      fillColor: '#E3F2FD',
      fillOpacity: 0.4,
      strokeColor: '#2196F3',
      strokeWidth: 2
    },
    text: { value: '网络设备组' }
  });

  // 绿色主题 - 服务器组
  lf.addNode({
    type: 'customGroup',
    x: 700,
    y: 200,
    properties: {
      width: 400,
      height: 300,
      fillColor: '#E8F5E9',
      fillOpacity: 0.4,
      strokeColor: '#4CAF50',
      strokeWidth: 2
    },
    text: { value: '服务器组' }
  });

  // 红色主题 - 防火墙组
  lf.addNode({
    type: 'customGroup',
    x: 1200,
    y: 200,
    properties: {
      width: 400,
      height: 300,
      fillColor: '#FFEBEE',
      fillOpacity: 0.4,
      strokeColor: '#F44336',
      strokeWidth: 2
    },
    text: { value: '防火墙组' }
  });
};

// ============================================
// 示例 3: 根据选中节点创建分组
// ============================================
export const createGroupFromSelection = (lf) => {
  const selectElements = lf.getSelectElements(true);

  if (!selectElements?.nodes || selectElements.nodes.length < 2) {
    console.warn('请至少选择2个节点');
    return null;
  }

  // 计算选中节点的边界
  let minX = Infinity, minY = Infinity;
  let maxX = -Infinity, maxY = -Infinity;

  selectElements.nodes.forEach(node => {
    const width = node.properties?.width || 60;
    const height = node.properties?.height || 60;
    minX = Math.min(minX, node.x - width / 2);
    minY = Math.min(minY, node.y - height / 2);
    maxX = Math.max(maxX, node.x + width / 2);
    maxY = Math.max(maxY, node.y + height / 2);
  });

  const padding = 30;
  const groupX = (minX + maxX) / 2;
  const groupY = (minY + maxY) / 2;
  const groupWidth = maxX - minX + padding * 2;
  const groupHeight = maxY - minY + padding * 2;

  // 创建分组
  const group = lf.addNode({
    type: 'customGroup',
    x: groupX,
    y: groupY,
    properties: {
      width: groupWidth,
      height: groupHeight,
      fillColor: '#E3F2FD',
      fillOpacity: 0.5,
      strokeColor: '#2196F3',
      strokeWidth: 2
    },
    text: {
      value: '新建分组',
      editable: true
    },
    children: selectElements.nodes.map(n => n.id)
  });

  return group;
};

// ============================================
// 示例 4: 动态修改分组样式
// ============================================
export const updateGroupStyle = (lf, groupId, theme = 'blue') => {
  const groupModel = lf.getNodeModelById(groupId);
  if (!groupModel) return;

  const themes = {
    blue: {
      fillColor: '#E3F2FD',
      fillOpacity: 0.5,
      strokeColor: '#2196F3',
      strokeWidth: 2
    },
    green: {
      fillColor: '#E8F5E9',
      fillOpacity: 0.5,
      strokeColor: '#4CAF50',
      strokeWidth: 2
    },
    red: {
      fillColor: '#FFEBEE',
      fillOpacity: 0.5,
      strokeColor: '#F44336',
      strokeWidth: 2
    },
    orange: {
      fillColor: '#FFF3E0',
      fillOpacity: 0.5,
      strokeColor: '#FF9800',
      strokeWidth: 2
    },
    purple: {
      fillColor: '#F3E5F5',
      fillOpacity: 0.5,
      strokeColor: '#9C27B0',
      strokeWidth: 2
    }
  };

  const style = themes[theme] || themes.blue;

  groupModel.setFillColor(style.fillColor);
  groupModel.setFillOpacity(style.fillOpacity);
  groupModel.setStrokeColor(style.strokeColor);
  groupModel.setStrokeWidth(style.strokeWidth);
};

// ============================================
// 示例 5: 创建半透明背景分组
// ============================================
export const createTransparentGroup = (lf) => {
  lf.addNode({
    type: 'customGroup',
    x: 400,
    y: 300,
    properties: {
      width: 500,
      height: 400,
      fillColor: '#000000',       // 黑色
      fillOpacity: 0.05,          // 5% 透明度，几乎透明
      strokeColor: '#666666',     // 灰色边框
      strokeWidth: 1
    },
    text: {
      value: '背景分组',
      editable: true
    }
  });
};

// ============================================
// 示例 6: 创建高亮分组
// ============================================
export const createHighlightGroup = (lf) => {
  lf.addNode({
    type: 'customGroup',
    x: 400,
    y: 300,
    properties: {
      width: 500,
      height: 400,
      fillColor: '#FFEB3B',       // 亮黄色
      fillOpacity: 0.3,           // 30% 透明度
      strokeColor: '#FFC107',     // 橙黄色边框
      strokeWidth: 3              // 较粗的边框
    },
    text: {
      value: '重点区域',
      editable: true
    }
  });
};

// ============================================
// 示例 7: 按类型批量创建分组
// ============================================
export const createGroupsByType = (lf, nodes) => {
  // 按节点类型分组
  const nodesByType = {};

  nodes.forEach(node => {
    const type = node.type || 'unknown';
    if (!nodesByType[type]) {
      nodesByType[type] = [];
    }
    nodesByType[type].push(node);
  });

  // 为每种类型创建分组
  const typeColors = {
    switch: { fill: '#E3F2FD', stroke: '#2196F3' },
    router: { fill: '#E8F5E9', stroke: '#4CAF50' },
    server: { fill: '#FFF3E0', stroke: '#FF9800' },
    firewall: { fill: '#FFEBEE', stroke: '#F44336' },
    pc: { fill: '#F3E5F5', stroke: '#9C27B0' }
  };

  Object.entries(nodesByType).forEach(([type, typeNodes]) => {
    if (typeNodes.length < 2) return; // 至少2个节点才创建分组

    // 计算边界
    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;

    typeNodes.forEach(node => {
      const width = node.properties?.width || 60;
      const height = node.properties?.height || 60;
      minX = Math.min(minX, node.x - width / 2);
      minY = Math.min(minY, node.y - height / 2);
      maxX = Math.max(maxX, node.x + width / 2);
      maxY = Math.max(maxY, node.y + height / 2);
    });

    const padding = 30;
    const colors = typeColors[type] || { fill: '#F5F5F5', stroke: '#9E9E9E' };

    lf.addNode({
      type: 'customGroup',
      x: (minX + maxX) / 2,
      y: (minY + maxY) / 2,
      properties: {
        width: maxX - minX + padding * 2,
        height: maxY - minY + padding * 2,
        fillColor: colors.fill,
        fillOpacity: 0.4,
        strokeColor: colors.stroke,
        strokeWidth: 2
      },
      text: {
        value: `${type} 组`,
        editable: true
      },
      children: typeNodes.map(n => n.id)
    });
  });
};

// ============================================
// 示例 8: 创建嵌套分组
// ============================================
export const createNestedGroups = (lf) => {
  // 外层分组 - 数据中心
  const outerGroup = lf.addNode({
    type: 'customGroup',
    x: 500,
    y: 400,
    properties: {
      width: 800,
      height: 600,
      fillColor: '#E8F5E9',
      fillOpacity: 0.3,
      strokeColor: '#4CAF50',
      strokeWidth: 3
    },
    text: {
      value: '数据中心',
      editable: true
    }
  });

  // 内层分组1 - Web服务器区
  lf.addNode({
    type: 'customGroup',
    x: 300,
    y: 300,
    properties: {
      width: 300,
      height: 200,
      fillColor: '#E3F2FD',
      fillOpacity: 0.5,
      strokeColor: '#2196F3',
      strokeWidth: 2
    },
    text: {
      value: 'Web服务器区',
      editable: true
    }
  });

  // 内层分组2 - 数据库区
  lf.addNode({
    type: 'customGroup',
    x: 700,
    y: 300,
    properties: {
      width: 300,
      height: 200,
      fillColor: '#FFF3E0',
      fillOpacity: 0.5,
      strokeColor: '#FF9800',
      strokeWidth: 2
    },
    text: {
      value: '数据库区',
      editable: true
    }
  });
};

// ============================================
// 示例 9: 交互式样式调整
// ============================================
export const createInteractiveStyleEditor = (lf, groupId) => {
  const groupModel = lf.getNodeModelById(groupId);
  if (!groupModel) return;

  // 返回样式控制器
  return {
    // 调整填充色
    setFillColor: (color) => groupModel.setFillColor(color),

    // 调整透明度
    setOpacity: (opacity) => groupModel.setFillOpacity(opacity),

    // 调整边框颜色
    setStrokeColor: (color) => groupModel.setStrokeColor(color),

    // 调整边框宽度
    setStrokeWidth: (width) => groupModel.setStrokeWidth(width),

    // 获取当前样式
    getStyle: () => ({
      fillColor: groupModel.properties.fillColor,
      fillOpacity: groupModel.properties.fillOpacity,
      strokeColor: groupModel.properties.strokeColor,
      strokeWidth: groupModel.properties.strokeWidth
    })
  };
};

// ============================================
// 示例 10: 应用预设主题
// ============================================
export const applyPresetTheme = (lf, groupId, presetName) => {
  const presets = {
    // 办公区域
    office: {
      fillColor: '#E8EAF6',
      fillOpacity: 0.4,
      strokeColor: '#3F51B5',
      strokeWidth: 2
    },
    // 生产环境
    production: {
      fillColor: '#FFEBEE',
      fillOpacity: 0.4,
      strokeColor: '#F44336',
      strokeWidth: 3
    },
    // 测试环境
    testing: {
      fillColor: '#FFF3E0',
      fillOpacity: 0.4,
      strokeColor: '#FF9800',
      strokeWidth: 2
    },
    // 开发环境
    development: {
      fillColor: '#E3F2FD',
      fillOpacity: 0.4,
      strokeColor: '#2196F3',
      strokeWidth: 2
    },
    // 安全区
    security: {
      fillColor: '#FCE4EC',
      fillOpacity: 0.5,
      strokeColor: '#E91E63',
      strokeWidth: 3
    },
    // 隔离区
    isolation: {
      fillColor: '#FFF9C4',
      fillOpacity: 0.6,
      strokeColor: '#FBC02D',
      strokeWidth: 2
    }
  };

  const groupModel = lf.getNodeModelById(groupId);
  if (!groupModel || !presets[presetName]) return;

  const preset = presets[presetName];
  groupModel.setFillColor(preset.fillColor);
  groupModel.setFillOpacity(preset.fillOpacity);
  groupModel.setStrokeColor(preset.strokeColor);
  groupModel.setStrokeWidth(preset.strokeWidth);
};

// ============================================
// 使用说明
// ============================================

/*
在 Vue 组件中使用:

import {
  createBasicGroup,
  createThemedGroups,
  createGroupFromSelection,
  updateGroupStyle,
  applyPresetTheme
} from '@/common/node/GroupNode.example.js';

// 在 LogicFlow 实例初始化后
const lf = new LogicFlow({ ... });

// 创建基本分组
createBasicGroup(lf);

// 创建主题分组
createThemedGroups(lf);

// 根据选中节点创建分组
const group = createGroupFromSelection(lf);

// 修改分组样式
if (group) {
  updateGroupStyle(lf, group.id, 'green');
}

// 应用预设主题
applyPresetTheme(lf, group.id, 'production');
*/
