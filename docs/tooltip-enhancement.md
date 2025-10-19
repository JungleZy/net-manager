# 控制按钮 Tooltip 提示功能文档

## 功能概述

为 Network.vue 页面右上角的所有控制按钮添加了 **Tooltip 文字提示**，提升用户体验和操作引导。

---

## 新增 Tooltip 提示

### 按钮列表与提示文字

| 序号 | 按钮功能         | 图标                         | Tooltip 文字                                                             | 触发位置 |
| ---- | ---------------- | ---------------------------- | ------------------------------------------------------------------------ | -------- |
| 1    | 刷新拓扑图       | 🔄 ReloadOutlined            | **刷新拓扑图**                                                           | bottom   |
| 2    | 居中显示         | 🎯 AimOutlined               | **居中显示**                                                             | bottom   |
| 3    | 全屏（下拉菜单） | ⛶ FullscreenOutlined         | **全屏**                                                                 | bottom   |
| 4    | 退出全屏         | ⛶ FullscreenExitOutlined     | **退出全屏**                                                             | bottom   |
| 5    | 主题切换         | 💡 BulbOutlined / BulbFilled | **动态文字**<br>• 暗黑模式：切换到明亮模式<br>• 明亮模式：切换到暗黑模式 | bottom   |

---

## 技术实现

### 1. 使用 Ant Design Vue Tooltip 组件

```vue
<a-tooltip title="提示文字" placement="bottom">
  <a-button>
    <!-- 按钮内容 -->
  </a-button>
</a-tooltip>
```

### 2. 各按钮实现代码

#### 刷新按钮

```vue
<a-tooltip title="刷新拓扑图" placement="bottom">
  <a-button
    @click="handleRefresh"
    :loading="loading"
    class="layout-center"
  >
    <template #icon>
      <ReloadOutlined />
    </template>
  </a-button>
</a-tooltip>
```

#### 居中按钮

```vue
<a-tooltip title="居中显示" placement="bottom">
  <a-button @click="handleCenter" class="layout-center">
    <template #icon>
      <AimOutlined />
    </template>
  </a-button>
</a-tooltip>
```

#### 全屏按钮（带下拉菜单）

```vue
<a-tooltip v-if="!isFullscreen" title="全屏" placement="bottom">
  <a-dropdown>
    <template #overlay>
      <a-menu @click="handleFullscreenMenuClick">
        <a-menu-item key="page">
          <template #icon>
            <FullscreenOutlined />
          </template>
          页内全屏
        </a-menu-item>
        <a-menu-item key="screen">
          <template #icon>
            <FullscreenOutlined />
          </template>
          屏幕全屏
        </a-menu-item>
      </a-menu>
    </template>
    <a-button class="layout-center">
      <template #icon>
        <FullscreenOutlined />
      </template>
    </a-button>
  </a-dropdown>
</a-tooltip>
```

#### 退出全屏按钮

```vue
<a-tooltip v-else title="退出全屏" placement="bottom">
  <a-button class="layout-center" @click="exitFullscreen">
    <template #icon>
      <FullscreenExitOutlined />
    </template>
  </a-button>
</a-tooltip>
```

#### 主题切换按钮（动态提示）

```vue
<a-tooltip
  :title="isDarkMode ? '切换到明亮模式' : '切换到暗黑模式'"
  placement="bottom"
>
  <a-button class="layout-center" @click="toggleTheme">
    <template #icon>
      <BulbOutlined v-if="isDarkMode" />
      <BulbFilled v-else />
    </template>
  </a-button>
</a-tooltip>
```

---

## 设计规范

### 1. Tooltip 位置

- **统一位置：** `placement="bottom"`（向下弹出）
- **原因：** 按钮位于页面右上角，向下弹出不会被遮挡

### 2. 提示文字规范

| 类型         | 规范                | 示例                                                   |
| ------------ | ------------------- | ------------------------------------------------------ |
| **静态提示** | 简短明确，动词+名词 | 刷新拓扑图、居中显示、全屏、退出全屏                   |
| **动态提示** | 根据状态变化        | 切换到明亮模式 ↔ 切换到暗黑模式                        |
| **字数控制** | 2-7 个汉字          | ✅ 刷新拓扑图<br>❌ 点击此按钮可以刷新当前的网络拓扑图 |

### 3. 交互体验

- **延迟显示：** Ant Design Vue 默认延迟 100ms
- **鼠标悬停触发：** 自动显示
- **移开鼠标隐藏：** 自动隐藏
- **不影响点击：** Tooltip 不阻碍按钮点击

---

## 视觉效果

### 默认样式（Ant Design Vue）

```
┌─────────────────┐
│   刷新拓扑图    │  ← Tooltip
└────────┬────────┘
         │
    ┌────▼────┐
    │    🔄   │       ← 按钮
    └─────────┘
```

### 暗黑模式适配

Tooltip 会自动适配暗黑模式：

- **明亮模式：** 深色背景 + 白色文字
- **暗黑模式：** 深色背景 + 浅色文字（Ant Design Vue 自动处理）

---

## 用户体验提升

### 1. 新用户引导

**问题：** 新用户不知道图标按钮的功能  
**解决：** Tooltip 提供即时的文字说明

### 2. 功能发现性

**问题：** 用户可能忽略某些功能（如全屏、主题切换）  
**解决：** 悬停时自动提示，增加功能曝光度

### 3. 操作确认

**问题：** 用户点击前不确定按钮功能  
**解决：** 先悬停查看提示，再决定是否点击

### 4. 减少误操作

**问题：** 图标相似可能导致误点  
**解决：** 提前查看 Tooltip，确认功能后再点击

---

## 兼容性

### 浏览器兼容性

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 14+

### 功能兼容性

- ✅ 与全屏功能兼容
- ✅ 与主题切换兼容
- ✅ 与刷新/居中功能兼容
- ✅ 与下拉菜单兼容（全屏按钮）
- ✅ 移动端自动禁用 Tooltip（触摸设备）

---

## 代码变更总结

### 修改的文件

- `dashboard/src/views/network/Network.vue`

### 新增的组件使用

- `<a-tooltip>` - Ant Design Vue Tooltip 组件

### 修改的按钮数量

- **总计：** 5 个按钮
- **静态提示：** 4 个（刷新、居中、全屏、退出全屏）
- **动态提示：** 1 个（主题切换）

---

## 测试建议

### 功能测试

1. ✅ 悬停在每个按钮上，验证 Tooltip 正确显示
2. ✅ 验证 Tooltip 文字内容准确无误
3. ✅ 验证 Tooltip 位置正确（向下弹出）
4. ✅ 点击按钮，验证功能正常且 Tooltip 消失

### 视觉测试

1. ✅ 明亮模式下 Tooltip 样式正常
2. ✅ 暗黑模式下 Tooltip 样式正常
3. ✅ Tooltip 文字清晰可读
4. ✅ Tooltip 不遮挡其他元素

### 交互测试

1. ✅ 鼠标快速移动时 Tooltip 不闪烁
2. ✅ 连续悬停多个按钮，Tooltip 切换流畅
3. ✅ 全屏/退出全屏切换时，Tooltip 正常显示
4. ✅ 主题切换时，Tooltip 文字动态更新

---

## 未来优化建议

### 1. 自定义 Tooltip 样式（可选）

如果需要统一的品牌风格：

```less
:deep(.ant-tooltip) {
  .ant-tooltip-inner {
    background-color: #1a1f3a;
    font-size: 12px;
    padding: 6px 12px;
  }

  .ant-tooltip-arrow-content {
    background-color: #1a1f3a;
  }
}
```

### 2. 快捷键提示（可选）

为支持快捷键的功能添加提示：

```vue
<a-tooltip title="居中显示 (Ctrl+0)" placement="bottom">
  <!-- 按钮 -->
</a-tooltip>
```

### 3. 长提示支持（可选）

对于复杂功能，可以使用多行提示：

```vue
<a-tooltip placement="bottom">
  <template #title>
    <div>刷新拓扑图</div>
    <div style="font-size: 11px; opacity: 0.8;">重新加载所有设备和连接</div>
  </template>
  <!-- 按钮 -->
</a-tooltip>
```

### 4. 禁用状态提示（可选）

为禁用的按钮添加说明：

```vue
<a-tooltip :title="loading ? '正在加载...' : '刷新拓扑图'" placement="bottom">
  <a-button :disabled="loading" @click="handleRefresh">
    <!-- 按钮内容 -->
  </a-button>
</a-tooltip>
```

---

## 常见问题

### Q1: Tooltip 不显示怎么办？

**A:** 检查以下几点：

1. 确认 Ant Design Vue 已正确安装
2. 检查按钮是否被其他元素遮挡
3. 验证 `placement` 属性是否正确

### Q2: Tooltip 位置不对怎么办？

**A:** 调整 `placement` 属性：

- `bottom` - 向下
- `top` - 向上
- `left` - 向左
- `right` - 向右

### Q3: 如何修改 Tooltip 延迟时间？

**A:** 使用 `mouseEnterDelay` 和 `mouseLeaveDelay` 属性：

```vue
<a-tooltip
  title="刷新拓扑图"
  placement="bottom"
  :mouseEnterDelay="0.5"
  :mouseLeaveDelay="0.2"
>
  <!-- 按钮 -->
</a-tooltip>
```

### Q4: 主题切换按钮的提示为什么是动态的？

**A:** 因为提示内容根据当前主题状态变化：

- 暗黑模式 → 提示"切换到明亮模式"
- 明亮模式 → 提示"切换到暗黑模式"

这样用户清楚地知道点击后会切换到什么模式。

---

## 版本历史

| 版本 | 日期       | 说明                                 |
| ---- | ---------- | ------------------------------------ |
| v1.0 | 2025-10-20 | 初始版本，为所有控制按钮添加 Tooltip |

---

**开发者：** Qoder AI  
**文档更新日期：** 2025-10-20  
**文档版本：** v1.0
