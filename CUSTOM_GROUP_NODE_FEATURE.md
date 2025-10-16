# 自定义分组节点功能说明

## 📋 概述

基于 LogicFlow 官方 `GroupNode.ts` 创建了自定义分组节点 `CustomGroupNode`，在**完整保留所有原有功能**的基础上，新增了**填充色**和**透明度**的自定义设置能力。

## 📁 相关文件

```
dashboard/src/common/node/
├── GroupNode.js           # 自定义分组节点实现
├── GroupNode.md          # 详细使用文档
├── GroupNode.example.js  # 10个使用示例
└── index.js              # 已更新导出配置
```

## ✨ 功能特性

### 保留的原有功能（100%兼容）

| 功能 | 说明 |
|------|------|
| ✅ 子节点管理 | 支持添加/删除子节点 (`addChild`/`removeChild`) |
| ✅ 折叠/展开 | 支持分组折叠功能 (`foldGroup`) |
| ✅ 拖拽限制 | 支持限制子节点移出分组 (`isRestrict`) |
| ✅ 虚拟边管理 | 折叠时自动管理连线显示 |
| ✅ 嵌套分组 | 支持分组嵌套 |
| ✅ 调整大小 | 支持分组尺寸调整 (`resizable`) |
| ✅ 文本编辑 | 支持分组名称编辑 |
| ✅ 历史记录 | 支持撤销/重做功能 |
| ✅ 范围判断 | `isInRange`/`isAllowMoveTo` 方法 |
| ✅ 锚点样式 | 自定义锚点样式 |

### 新增功能

| 功能 | 属性名 | 类型 | 默认值 | 说明 |
|------|--------|------|--------|------|
| 🎨 填充色 | `fillColor` | `string` | `'#F4F5F6'` | 支持任何 CSS 颜色格式 |
| 🌈 透明度 | `fillOpacity` | `number` | `0.3` | 范围 0-1，支持透明效果 |
| 🖌️ 边框颜色 | `strokeColor` | `string` | `'#CECECE'` | 边框颜色设置 |
| 📏 边框宽度 | `strokeWidth` | `number` | `2` | 边框粗细（像素） |

### 新增方法

```javascript
// 设置填充颜色
groupModel.setFillColor('#E3F2FD');

// 设置透明度（0-1）
groupModel.setFillOpacity(0.5);

// 设置边框颜色
groupModel.setStrokeColor('#2196F3');

// 设置边框宽度
groupModel.setStrokeWidth(2);
```

## 🚀 快速开始

### 1. 注册节点（已自动完成）

节点已在 `index.js` 中导出，LogicFlow 初始化时会自动注册。

### 2. 创建分组

```javascript
lf.addNode({
  type: 'customGroup',
  x: 300,
  y: 200,
  properties: {
    width: 400,
    height: 300,
    fillColor: '#E3F2FD',      // 填充色
    fillOpacity: 0.5,           // 透明度
    strokeColor: '#2196F3',     // 边框色
    strokeWidth: 2              // 边框宽度
  },
  text: {
    value: '我的分组',
    editable: true
  }
});
```

### 3. 修改样式

```javascript
const groupModel = lf.getNodeModelById('group-id');
groupModel.setFillColor('#E8F5E9');
groupModel.setFillOpacity(0.6);
```

## 🎨 预设主题配色

### 网络设备分组
```javascript
{
  fillColor: '#E3F2FD',    // 浅蓝色
  fillOpacity: 0.4,
  strokeColor: '#2196F3',  // 蓝色
  strokeWidth: 2
}
```

### 服务器分组
```javascript
{
  fillColor: '#E8F5E9',    // 浅绿色
  fillOpacity: 0.4,
  strokeColor: '#4CAF50',  // 绿色
  strokeWidth: 2
}
```

### 安全设备分组
```javascript
{
  fillColor: '#FFEBEE',    // 浅红色
  fillOpacity: 0.4,
  strokeColor: '#F44336',  // 红色
  strokeWidth: 2
}
```

### 生产环境
```javascript
{
  fillColor: '#FFEBEE',    // 浅红色
  fillOpacity: 0.4,
  strokeColor: '#F44336',  // 红色
  strokeWidth: 3           // 粗边框强调重要性
}
```

### 测试环境
```javascript
{
  fillColor: '#FFF3E0',    // 浅橙色
  fillOpacity: 0.4,
  strokeColor: '#FF9800',  // 橙色
  strokeWidth: 2
}
```

### 开发环境
```javascript
{
  fillColor: '#E3F2FD',    // 浅蓝色
  fillOpacity: 0.4,
  strokeColor: '#2196F3',  // 蓝色
  strokeWidth: 2
}
```

## 📚 示例代码

项目提供了 **10 个完整示例**，位于 `GroupNode.example.js`：

1. ✅ 创建基本分组
2. ✅ 创建不同主题的分组
3. ✅ 根据选中节点创建分组
4. ✅ 动态修改分组样式
5. ✅ 创建半透明背景分组
6. ✅ 创建高亮分组
7. ✅ 按类型批量创建分组
8. ✅ 创建嵌套分组
9. ✅ 交互式样式调整
10. ✅ 应用预设主题

## 🔧 技术实现

### 架构设计

```
CustomGroupNodeModel (extends RectResizeModel)
├── 继承所有 GroupNode 原有功能
├── 新增样式属性 (fillColor, fillOpacity, strokeColor, strokeWidth)
├── 重写 getNodeStyle() 应用自定义样式
└── 新增样式设置方法

CustomGroupNode (extends RectResizeView)
├── 保留原有渲染逻辑
├── 支持折叠图标显示
├── 支持可添加状态显示
└── 支持调整大小控制点
```

### 核心代码片段

```javascript
// 初始化样式属性
initNodeData(data) {
  super.initNodeData(data);
  // ... 原有逻辑 ...
  
  // 新增样式初始化
  if (this.properties.fillColor === undefined) {
    this.properties.fillColor = '#F4F5F6';
  }
  if (this.properties.fillOpacity === undefined) {
    this.properties.fillOpacity = 0.3;
  }
}

// 应用自定义样式
getNodeStyle() {
  const style = super.getNodeStyle();
  const { fillColor, fillOpacity, strokeColor, strokeWidth } = this.properties;
  
  return {
    ...style,
    fill: fillColor || '#F4F5F6',
    fillOpacity: fillOpacity !== undefined ? fillOpacity : 0.3,
    stroke: strokeColor || '#CECECE',
    strokeWidth: strokeWidth !== undefined ? strokeWidth : 2,
  };
}
```

## 📖 在拓扑图中使用

在 `Topology.vue` 中已经自动导入并注册，可以直接使用：

```javascript
// 在 handleCreateGroup 方法中使用
const handleCreateGroup = (lfInstance) => {
  // ... 获取选中节点 ...
  
  // 创建自定义分组
  lfInstance.addNode({
    type: 'customGroup',  // 使用 customGroup 类型
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
    }
  });
};
```

## ⚠️ 注意事项

1. **透明度范围**：`fillOpacity` 必须在 0-1 之间
2. **颜色格式**：支持所有 CSS 颜色格式（如 `#RGB`、`rgb()`、颜色名称等）
3. **性能考虑**：过多半透明元素可能影响渲染性能
4. **兼容性**：与原生 GroupNode 完全兼容，可无缝替换
5. **类型名称**：注册类型为 `customGroup`，不是 `group`

## 📊 对比原有功能

| 特性 | 原 GroupNode | CustomGroupNode |
|------|--------------|-----------------|
| 子节点管理 | ✅ | ✅ |
| 折叠/展开 | ✅ | ✅ |
| 虚拟边管理 | ✅ | ✅ |
| 嵌套分组 | ✅ | ✅ |
| 调整大小 | ✅ | ✅ |
| 文本编辑 | ✅ | ✅ |
| **填充色设置** | ❌ | ✅ |
| **透明度设置** | ❌ | ✅ |
| **边框颜色设置** | ❌ | ✅ |
| **边框宽度设置** | ❌ | ✅ |

## 🎯 使用场景

1. **网络拓扑图** - 使用不同颜色区分不同网络区域
2. **机房布局** - 使用颜色标识不同设备区域
3. **流程图分组** - 使用颜色区分不同业务流程
4. **组织架构图** - 使用颜色标识不同部门
5. **数据中心规划** - 使用颜色区分生产/测试/开发环境

## 📝 更新日志

### v1.0.0 (2025-10-16)
- ✅ 基于官方 GroupNode.ts 创建自定义节点
- ✅ 新增填充色设置功能 (`fillColor`)
- ✅ 新增透明度设置功能 (`fillOpacity`)
- ✅ 新增边框颜色设置功能 (`strokeColor`)
- ✅ 新增边框宽度设置功能 (`strokeWidth`)
- ✅ 提供完整的 API 方法
- ✅ 提供 10 个使用示例
- ✅ 提供详细文档说明
- ✅ 100% 兼容原有 GroupNode 功能

## 🔗 参考资料

- [LogicFlow 官方文档](https://docs.logic-flow.cn/)
- [GroupNode 扩展文档](https://docs.logic-flow.cn/guide/extension/group)
- 源文件：`dashboard/node_modules/@logicflow/extension/src/materials/group/GroupNode.ts`
- 实现文件：`dashboard/src/common/node/GroupNode.js`
- 文档文件：`dashboard/src/common/node/GroupNode.md`
- 示例文件：`dashboard/src/common/node/GroupNode.example.js`
