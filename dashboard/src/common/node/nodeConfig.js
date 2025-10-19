/**
 * 节点通用配置文件
 * 统一管理所有节点的颜色、样式等配置
 */

// 冻结颜色配置，避免运行时修改
export const NODE_COLORS = Object.freeze({
  ONLINE_PRIMARY: '#B5D6FB',
  ONLINE_SECONDARY: '#1677FF',
  OFFLINE_PRIMARY: '#ffffff',
  OFFLINE_SECONDARY: '#999999',
  WHITE: '#FFFFFF'
});

/**
 * 根据节点状态获取颜色配置
 * @param {string} status - 节点状态 ('online' | 'offline')
 * @returns {Object} 包含 primary 和 secondary 颜色的对象
 */
export const getNodeColors = (status) => {
  return status === 'offline' || !status
    ? {
      primary: NODE_COLORS.OFFLINE_PRIMARY,
      secondary: NODE_COLORS.OFFLINE_SECONDARY
    }
    : {
      primary: NODE_COLORS.ONLINE_PRIMARY,
      secondary: NODE_COLORS.ONLINE_SECONDARY
    };
};

// 默认样式配置
export const DEFAULT_STYLES = Object.freeze({
  TEXT_FILL_LIGHT: '#333',      // 明亮模式文字颜色
  TEXT_FILL_DARK: '#ffffff',    // 暗黑模式文字颜色
  DEFAULT_FONT_SIZE: 12,
  ONLINE_COLOR: '#0276F7',
  OFFLINE_COLOR: 'red'
});

// 当前主题状态（由外部设置）
let currentTheme = 'light';

/**
 * 设置当前主题模式
 * @param {string} theme - 主题模式 ('light' | 'dark')
 */
export const setTheme = (theme) => {
  currentTheme = theme;
};

/**
 * 获取当前主题下的文字颜色
 * @returns {string} 文字颜色值
 */
export const getTextFillColor = () => {
  return currentTheme === 'dark' ? DEFAULT_STYLES.TEXT_FILL_DARK : DEFAULT_STYLES.TEXT_FILL_LIGHT;
};
