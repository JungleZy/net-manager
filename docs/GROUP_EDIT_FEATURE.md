# 分组框右键编辑功能

## 功能概述

为拓扑图中的分组框（customGroup）添加了右键编辑功能，用户可以通过右键点击分组框打开编辑模态框，修改分组的各项属性。

## 功能特性

### 1. 右键触发
- 在任意 `customGroup` 类型的节点上右键点击
- 自动阻止浏览器默认右键菜单
- 打开分组编辑模态框

### 2. 可编辑属性

#### 2.1 分组名称
- 支持自定义分组名称
- 名称显示在分组框顶部

#### 2.2 背景颜色
- 使用颜色选择器选择背景色
- 支持手动输入十六进制颜色值（如 #F4F5F6）
- 默认颜色：#F4F5F6

#### 2.3 背景透明度
- 使用滑块调整透明度（0-100%）
- 范围：0.0 - 1.0
- 默认透明度：0.3 (30%)

#### 2.4 边框颜色
- 使用颜色选择器选择边框颜色
- 支持手动输入十六进制颜色值
- 默认颜色：#CECECE

#### 2.5 边框宽度
- 使用数字输入框设置边框宽度
- 范围：1-10 像素
- 默认宽度：2px

#### 2.6 边框样式
- **实线**：默认样式，strokeDasharray = ''
- **虚线**：strokeDasharray = '5,5'
- **点线**：strokeDasharray = '2,2'

## 技术实现

### 1. 核心文件修改

#### 1.1 Topology.vue
- 添加分组编辑模态框组件
- 添加右键事件监听 (`node:contextmenu`)
- 实现分组属性更新逻辑

#### 1.2 GroupNode.js
- 扩展 `CustomGroupNodeModel` 支持 `strokeDasharray` 属性
- 更新 `getNodeStyle()` 方法应用边框样式
- 添加 `setStrokeDasharray()` 方法

### 2. 状态管理

```javascript
// 模态框状态
const showGroupEditModal = ref(false)
const currentEditingGroupId = ref(null)

// 编辑表单数据
const groupEditForm = ref({
  name: '',
  fillColor: '#F4F5F6',
  fillOpacity: 0.3,
  strokeColor: '#CECECE',
  strokeWidth: 2,
  strokeDasharray: '' // 空字符串=实线，'5,5'=虚线，'2,2'=点线
})
```

### 3. 事件处理

#### 3.1 右键点击事件
```javascript
lf.on('node:contextmenu', ({ data, e }) => {
  if (data && data.type === 'customGroup') {
    e.preventDefault()
    handleGroupRightClick(data)
  }
})
```

#### 3.2 样式更新策略
根据历史经验，LogicFlow 中直接使用 `setProperty` 更新分组样式可能失效，因此采用**删除重建**策略：

1. 保存分组的所有属性（位置、尺寸、子节点等）
2. 删除原分组节点
3. 使用相同 ID 重新创建分组节点
4. 应用新的样式属性

```javascript
// 删除旧分组
lf.deleteNode(currentEditingGroupId.value)

// 在下一个 tick 中重建
nextTick(() => {
  lf.addNode({
    id: currentEditingGroupId.value,
    type: 'customGroup',
    x, y,
    properties: {
      ...properties,
      fillColor: groupEditForm.value.fillColor,
      fillOpacity: groupEditForm.value.fillOpacity,
      strokeColor: groupEditForm.value.strokeColor,
      strokeWidth: groupEditForm.value.strokeWidth,
      strokeDasharray: groupEditForm.value.strokeDasharray
    },
    text: { value: groupEditForm.value.name },
    children: children || []
  })
})
```

## 使用方法

### 步骤 1: 创建分组
1. 选择至少2个节点
2. 点击工具栏的"分组"按钮（📦）
3. 分组创建成功，显示默认名称"新建分组"

### 步骤 2: 编辑分组
1. 在分组框上右键点击
2. 在弹出的模态框中修改属性：
   - 修改分组名称
   - 选择背景颜色
   - 调整背景透明度
   - 选择边框颜色
   - 设置边框宽度
   - 选择边框样式（实线/虚线/点线）
3. 点击"确定"保存修改

### 步骤 3: 保存拓扑图
- 点击右下角"保存"按钮
- 分组样式将持久化到数据库

## UI 组件

### 模态框表单

```vue
<a-modal
  v-model:open="showGroupEditModal"
  title="编辑分组"
  :width="500"
>
  <!-- 分组名称 -->
  <a-input v-model:value="groupEditForm.name" />
  
  <!-- 背景颜色 -->
  <input type="color" v-model="groupEditForm.fillColor" />
  <a-input v-model:value="groupEditForm.fillColor" />
  
  <!-- 背景透明度 -->
  <a-slider v-model:value="groupEditForm.fillOpacity" :min="0" :max="1" :step="0.1" />
  
  <!-- 边框颜色 -->
  <input type="color" v-model="groupEditForm.strokeColor" />
  <a-input v-model:value="groupEditForm.strokeColor" />
  
  <!-- 边框宽度 -->
  <a-input-number v-model:value="groupEditForm.strokeWidth" :min="1" :max="10" />
  
  <!-- 边框样式 -->
  <a-radio-group v-model:value="groupEditForm.strokeDasharray">
    <a-radio value="">实线</a-radio>
    <a-radio value="5,5">虚线</a-radio>
    <a-radio value="2,2">点线</a-radio>
  </a-radio-group>
</a-modal>
```

## 样式定义

```less
.group-edit-form {
  .form-item {
    margin-bottom: 16px;
    
    .form-label {
      display: block;
      margin-bottom: 8px;
      font-size: 14px;
      font-weight: 500;
      color: #333;
    }
    
    .color-picker-wrapper {
      display: flex;
      gap: 8px;
      
      .color-input {
        width: 60px;
        height: 32px;
        border: 1px solid #d9d9d9;
        border-radius: 4px;
        cursor: pointer;
      }
    }
  }
}
```

## 数据结构

### 分组节点数据格式

```javascript
{
  id: 'group_xxx',
  type: 'customGroup',
  x: 400,
  y: 300,
  properties: {
    width: 500,
    height: 300,
    fillColor: '#F4F5F6',      // 背景色
    fillOpacity: 0.3,           // 透明度
    strokeColor: '#CECECE',     // 边框色
    strokeWidth: 2,             // 边框宽度
    strokeDasharray: '5,5'      // 边框样式
  },
  text: {
    x: 400,
    y: 150,
    value: '新建分组',
    editable: true
  },
  children: ['node1', 'node2'] // 子节点ID列表
}
```

## 注意事项

### 1. 兼容性
- 仅支持 `customGroup` 类型的分组节点
- 原生 LogicFlow 的 `group` 类型不支持此功能

### 2. 样式更新
- 使用删除重建策略确保样式正确应用
- 保留子节点和位置信息

### 3. 边框样式格式
- strokeDasharray 使用 SVG 标准格式
- 格式：`'间隔1,间隔2'`
- 示例：
  - `''` - 实线
  - `'5,5'` - 5px 实线，5px 空白
  - `'2,2'` - 2px 实线，2px 空白
  - `'10,5,2,5'` - 复杂虚线模式

## 测试建议

### 1. 功能测试
- [ ] 右键点击分组是否弹出模态框
- [ ] 修改各项属性是否生效
- [ ] 边框样式切换是否正常
- [ ] 保存后重新加载是否保持样式

### 2. 边界测试
- [ ] 空分组名称处理
- [ ] 颜色值格式验证
- [ ] 透明度边界值（0 和 1）
- [ ] 边框宽度边界值（1 和 10）

### 3. 交互测试
- [ ] 模态框取消操作
- [ ] 修改后未保存的提示
- [ ] 多次编辑同一分组
- [ ] 编辑不同分组切换

## 扩展功能建议

### 1. 快捷操作
- 添加预设配色方案
- 支持样式复制/粘贴
- 批量修改多个分组

### 2. 高级样式
- 支持圆角设置
- 支持阴影效果
- 支持渐变背景

### 3. 右键菜单
- 添加完整的右键上下文菜单
- 包含编辑、删除、复制等操作

## 相关文件

- `dashboard/src/views/topology/Topology.vue` - 主组件
- `dashboard/src/common/node/GroupNode.js` - 分组节点定义
- `GROUP_EDIT_FEATURE.md` - 本文档

## 版本历史

- **v1.0.0** (2025-10-16)
  - 初始版本
  - 支持右键编辑分组
  - 支持背景色、透明度、边框色、边框宽度、边框样式设置
