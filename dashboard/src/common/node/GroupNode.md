# 自定义分组节点 (CustomGroupNode)

## 概述

`CustomGroupNode` 是基于 LogicFlow 官方 `GroupNode` 扩展的自定义分组节点，在保留所有原有功能的基础上，新增了**填充色设置**和**透明度设置**功能。

## 功能特性

### 原有功能（完整保留）
- ✅ 分组子节点管理（添加/删除子节点）
- ✅ 分组折叠/展开功能
- ✅ 子节点拖拽限制
- ✅ 虚拟边管理（折叠时的连线处理）
- ✅ 嵌套分组支持
- ✅ 分组调整大小
- ✅ 分组文本编辑
- ✅ 历史记录支持

### 新增功能
- 🎨 **填充色设置** - 支持自定义分组背景颜色
- 🌈 **透明度设置** - 支持自定义分组背景透明度（0-1）
- 🖌️ **边框颜色设置** - 支持自定义边框颜色
- 📏 **边框宽度设置** - 支持自定义边框粗细

## 使用方法

### 1. 基本使用

```javascript
import { LogicFlow } from '@logicflow/core';
import GroupNode from '@/common/node/GroupNode';

// 初始化 LogicFlow
const lf = new LogicFlow({
  container: document.querySelector('#container'),
  // ... 其他配置
});

// 注册自定义分组节点
lf.register(GroupNode);

// 创建分组节点
lf.addNode({
  type: 'customGroup',
  x: 300,
  y: 200,
  properties: {
    width: 400,
    height: 300,
    fillColor: '#E3F2FD',      // 填充色
    fillOpacity: 0.5,           // 透明度
    strokeColor: '#2196F3',     // 边框颜色
    strokeWidth: 2              // 边框宽度
  },
  text: {
    value: '我的分组',
    editable: true
  },
  children: [] // 子节点ID列表
});
```

### 2. 动态修改样式

```javascript
// 获取分组节点模型
const groupModel = lf.getNodeModelById('group-node-id');

// 修改填充色
groupModel.setFillColor('#FFEBEE');

// 修改透明度
groupModel.setFillOpacity(0.8);

// 修改边框颜色
groupModel.setStrokeColor('#F44336');

// 修改边框宽度
groupModel.setStrokeWidth(3);
```

### 3. 完整示例

```javascript
// 创建一个带有完整样式配置的分组
const groupData = {
  type: 'customGroup',
  x: 400,
  y: 300,
  properties: {
    // 尺寸设置
    width: 500,
    height: 400,
    
    // 样式设置（新增）
    fillColor: '#E8F5E9',       // 浅绿色填充
    fillOpacity: 0.6,            // 60% 透明度
    strokeColor: '#4CAF50',      // 绿色边框
    strokeWidth: 2,              // 边框宽度 2px
    
    // 功能设置
    isFolded: false,             // 展开状态
    groupAddable: false          // 是否可添加子节点
  },
  text: {
    x: 400,
    y: 280,
    value: '服务器组',
    editable: true,
    draggable: false
  },
  children: ['node1', 'node2', 'node3'] // 子节点ID列表
};

lf.addNode(groupData);
```

## 属性说明

### Properties 配置项

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `fillColor` | `string` | `'#F4F5F6'` | 填充颜色（支持任何 CSS 颜色格式） |
| `fillOpacity` | `number` | `0.3` | 填充透明度（0-1，0为完全透明，1为完全不透明） |
| `strokeColor` | `string` | `'#CECECE'` | 边框颜色 |
| `strokeWidth` | `number` | `2` | 边框宽度（像素） |
| `width` | `number` | `500` | 分组宽度 |
| `height` | `number` | `300` | 分组高度 |
| `isFolded` | `boolean` | `false` | 是否折叠 |
| `groupAddable` | `boolean` | `false` | 是否显示可添加提示 |

### 方法说明

| 方法名 | 参数 | 返回值 | 说明 |
|--------|------|--------|------|
| `setFillColor(color)` | `color: string` | `void` | 设置填充颜色 |
| `setFillOpacity(opacity)` | `opacity: number` | `void` | 设置填充透明度 |
| `setStrokeColor(color)` | `color: string` | `void` | 设置边框颜色 |
| `setStrokeWidth(width)` | `width: number` | `void` | 设置边框宽度 |
| `addChild(id)` | `id: string` | `void` | 添加子节点 |
| `removeChild(id)` | `id: string` | `void` | 删除子节点 |
| `foldGroup(isFolded)` | `isFolded: boolean` | `void` | 折叠/展开分组 |

## 颜色配置示例

### 预设主题配色

```javascript
// 蓝色主题
{
  fillColor: '#E3F2FD',
  fillOpacity: 0.5,
  strokeColor: '#2196F3',
  strokeWidth: 2
}

// 绿色主题
{
  fillColor: '#E8F5E9',
  fillOpacity: 0.5,
  strokeColor: '#4CAF50',
  strokeWidth: 2
}

// 红色主题
{
  fillColor: '#FFEBEE',
  fillOpacity: 0.5,
  strokeColor: '#F44336',
  strokeWidth: 2
}

// 橙色主题
{
  fillColor: '#FFF3E0',
  fillOpacity: 0.5,
  strokeColor: '#FF9800',
  strokeWidth: 2
}

// 紫色主题
{
  fillColor: '#F3E5F5',
  fillOpacity: 0.5,
  strokeColor: '#9C27B0',
  strokeWidth: 2
}

// 半透明样式
{
  fillColor: '#000000',
  fillOpacity: 0.1,
  strokeColor: '#666666',
  strokeWidth: 1
}
```

## 在拓扑图中使用

在 `Topology.vue` 中使用自定义分组节点：

```javascript
// 已自动导入并注册，无需额外操作

// 创建分组的示例方法
const createCustomGroup = () => {
  const selectElements = lf.getSelectElements(true);
  
  if (!selectElements?.nodes || selectElements.nodes.length < 2) {
    message.warning('请至少选择2个节点来创建分组');
    return;
  }

  // 计算边界
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

  // 创建自定义分组
  lf.addNode({
    type: 'customGroup',
    x: groupX,
    y: groupY,
    properties: {
      width: groupWidth,
      height: groupHeight,
      fillColor: '#E3F2FD',    // 自定义填充色
      fillOpacity: 0.4,         // 自定义透明度
      strokeColor: '#2196F3',   // 自定义边框色
      strokeWidth: 2
    },
    text: {
      value: '新建分组',
      editable: true
    },
    children: selectElements.nodes.map(n => n.id)
  });
};
```

## 注意事项

1. **透明度范围**：`fillOpacity` 的有效范围是 0-1，超出此范围可能导致不可预期的显示效果
2. **颜色格式**：支持所有 CSS 颜色格式（如 `#RGB`、`#RRGGBB`、`rgb()`、`rgba()`、颜色名称等）
3. **性能考虑**：过多的半透明元素可能影响渲染性能，建议合理使用
4. **兼容性**：与原生 GroupNode 完全兼容，可无缝替换使用

## 技术实现

- 继承自 `@logicflow/extension` 的 `RectResizeModel` 和 `RectResizeView`
- 重写 `getNodeStyle()` 方法以应用自定义样式
- 新增样式设置方法（`setFillColor`、`setFillOpacity` 等）
- 保留所有原有的分组功能逻辑
