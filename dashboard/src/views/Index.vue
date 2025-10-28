<template>
  <div class="size-full main">
    <div
      class="h-[52px] bg-blue-600 px-[20px] w-full shadow-md layout-side title"
    >
      <!-- Logo部分 -->
      <div class="h-full layout-left-center">
        <div class="text-2xl font-bold h-full layout-left-center text-white">
          网络监控中心
        </div>

        <!-- 菜单部分 -->
        <div class="flex h-full ml-[24px]">
          <div
            class="h-full layout-left-center px-[12px] cursor-pointer menu-item border-b-3"
            :class="
              $route.path === '/home' || $route.path === '/'
                ? 'text-white menu-item-active'
                : ''
            "
            @click="switchTo('/home')"
          >
            监控面板
          </div>
          <div
            class="h-full layout-left-center px-[12px] cursor-pointer menu-item border-b-3"
            :class="
              $route.path === '/network' ? 'text-white menu-item-active' : ''
            "
            @click="switchTo('/network')"
          >
            网络拓扑
          </div>
          <div
            class="h-full layout-left-center px-[12px] cursor-pointer menu-item border-b-3"
            :class="
              $route.path === '/devices' ? 'text-white menu-item-active' : ''
            "
            @click="switchTo('/devices')"
          >
            设备管理
          </div>
          <div
            class="h-full layout-left-center px-[12px] cursor-pointer menu-item border-b-3"
            :class="
              $route.path === '/topology' ? 'text-white menu-item-active' : ''
            "
            @click="switchTo('/topology')"
          >
            拓扑管理
          </div>
        </div>
      </div>

      <div class="h-full layout-right-center">
        <div
          class="h-full layout-center cursor-pointer text-sm mr-[16px]"
          @click="openGuideModal"
        >
          使用指南
        </div>
        <div
          class="h-full layout-center cursor-pointer text-sm"
          @click="openAgentModal"
        >
          <DownloadOutlined class="mr-[2px]" />下载探针
        </div>
      </div>
    </div>
    <div class="h-[calc(100vh-52px)]">
      <!-- 路由出口 -->
      <router-view></router-view>
    </div>
    <a-modal
      v-model:open="agentVisible"
      width="724px"
      centered
      title="下载探针"
      :footer="null"
    >
      <AgentDownload />
    </a-modal>

    <a-modal
      v-model:open="guideVisible"
      width="960px"
      centered
      title="使用指南"
      :footer="null"
      :destroyOnClose="true"
      :body-style="{ height: '80vh', overflowY: 'auto' }"
    >
      <div v-if="guideLoading" class="text-gray-500">加载中...</div>
      <div v-else class="guide-layout">
        <div ref="tocSidebar" class="toc-sidebar">
          <div class="toc-title">目录</div>
          <ul class="toc-list" v-if="tocItems.length">
            <li
              v-for="(it, i) in tocItems"
              :key="i"
              :style="{ marginLeft: `${(it.level - 1) * 12}px` }"
            >
              <a :href="`#${enc(it.id)}`">{{ it.text }}</a>
            </li>
          </ul>
          <div v-else class="empty-toc">目录生成中...</div>
        </div>
        <div ref="guideContainer" class="markdown" v-html="guideHtml"></div>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { onMounted, ref, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DownloadOutlined } from '@ant-design/icons-vue'
import AgentDownload from '@/components/agent/AgentDownload.vue'
import MarkdownIt from 'markdown-it'
import { full as emoji } from 'markdown-it-emoji'
import taskLists from 'markdown-it-task-lists'
import anchor from 'markdown-it-anchor'
// highlight.js 与样式将按需在运行时懒加载

// 获取路由信息
const route = useRoute()
const router = useRouter()
const agentVisible = ref(false)
const guideVisible = ref(false)
const guideLoading = ref(false)
const guideHtml = ref('')
const rawMarkdown = ref('')
const guideContainer = ref(null)
const tocSidebar = ref(null)
const tocItems = ref([])

// 文档大小阈值与高亮策略
const LARGE_DOC_THRESHOLD = 50 * 1024 // 50KB
let isLargeDoc = false
const COMMON_LANGS = new Set([
  'json',
  'bash',
  'shell',
  'sh',
  'yaml',
  'yml',
  'js',
  'javascript',
  'ts',
  'typescript',
  'py',
  'python'
])

// 懒加载 highlight.js 与样式
let hljsLib = null
const ensureHljsStyle = () => {
  if (document.getElementById('hljs-style')) return
  const link = document.createElement('link')
  link.id = 'hljs-style'
  link.rel = 'stylesheet'
  link.href = 'https://unpkg.com/highlight.js@11.9.0/styles/github-dark.min.css'
  document.head.appendChild(link)
}
const ensureHLJS = async () => {
  if (hljsLib) return hljsLib
  const mod = await import('highlight.js')
  hljsLib = mod.default || mod
  ensureHljsStyle()
  return hljsLib
}

// 简易转义（用于未指定语言的代码块内容）
const escapeHtml = (s) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

// slug 化工具，与目录及锚点保持一致
const slugify = (s) =>
  s
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\u4e00-\u9fa5\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')

// 收集 Markdown 中代码围栏语言（用于决定是否加载高亮库）
const collectFenceLangs = (text) => {
  const langs = new Set()
  const re = /^```(\w+)/gm
  let m
  while ((m = re.exec(text)) !== null) {
    langs.add((m[1] || '').toLowerCase())
  }
  return langs
}

// 使用 markdown-it 渲染 Markdown；禁用自动检测，仅在需要时高亮
const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: false,
  highlight: (str, lang) => {
    try {
      const l = (lang || '').toLowerCase()
      if (l) {
        if (isLargeDoc && !COMMON_LANGS.has(l)) {
          return escapeHtml(str)
        }
        const lib = hljsLib && (hljsLib.highlight ? hljsLib : hljsLib.default)
        if (
          lib &&
          typeof lib.getLanguage === 'function' &&
          lib.getLanguage(l)
        ) {
          return lib.highlight(str, { language: l, ignoreIllegals: true }).value
        }
      }
      return escapeHtml(str)
    } catch (e) {
      return escapeHtml(str)
    }
  }
})
const defaultLinkOpen =
  md.renderer.rules.link_open ||
  function (tokens, idx, options, env, self) {
    return self.renderToken(tokens, idx, options)
  }
// 仅对外部 http(s) 链接添加 target=_blank，# 锚点与相对链接不加
md.renderer.rules.link_open = function (tokens, idx, options, env, self) {
  const hrefIndex = tokens[idx].attrIndex('href')
  const href = hrefIndex >= 0 ? tokens[idx].attrs[hrefIndex][1] : ''
  const isExternal = /^https?:\/\//i.test(href)
  if (isExternal) {
    const targetIndex = tokens[idx].attrIndex('target')
    if (targetIndex < 0) tokens[idx].attrPush(['target', '_blank'])
    const relIndex = tokens[idx].attrIndex('rel')
    if (relIndex < 0) tokens[idx].attrPush(['rel', 'noopener'])
  }
  return defaultLinkOpen(tokens, idx, options, env, self)
}

// 启用 emoji、任务列表、目录 (TOC) 与锚点
md.use(emoji)
md.use(taskLists, { enabled: true })
md.use(anchor, {
  permalink: anchor.permalink.linkInsideHeader({
    symbol: '¶',
    placement: 'after',
    class: 'header-anchor'
  }),
  slugify
})

// 让代码块的 <code> 添加 hljs 类，以应用主题样式
const fence =
  md.renderer.rules.fence ||
  ((tokens, idx, options, env, self) => self.renderToken(tokens, idx, options))
md.renderer.rules.fence = (tokens, idx, options, env, self) => {
  const token = tokens[idx]
  const langName = token.info.trim().split(/\s+/g)[0]
  const highlighted = options.highlight
    ? options.highlight(token.content, langName)
    : token.content
  const classAttr = langName
    ? ` class="hljs language-${langName}"`
    : ' class="hljs"'
  return `<pre><code${classAttr}>${highlighted}</code></pre>`
}

// 页面切换方法
const switchTo = (path) => {
  router.push(path)
}
const openAgentModal = () => {
  agentVisible.value = true
}

const esc = (s) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
// 直接从 Markdown 文本解析标题，快速生成目录
const parseHeadingsFromMd = (text) => {
  const lines = text.split(/\n+/)
  const items = []
  for (const ln of lines) {
    const m = /^(#{1,6})\s+(.+)$/.exec(ln.trim())
    if (!m) continue
    const level = m[1].length
    const title = m[2].replace(/#+\s*$/, '').trim()
    const id = slugify(title)
    items.push({ level, id, text: title })
  }
  return items
}
const openGuideModal = async () => {
  guideVisible.value = true
  guideLoading.value = true
  try {
    const t0 = performance.now()
    const res = await fetch('/docs/使用说明-聚合.md')
    if (!res.ok) throw new Error('无法加载文档')
    const text = await res.text()
    const tFetch = performance.now()
    rawMarkdown.value = text
    // 评估文档大小并按需加载高亮
    isLargeDoc = text.length > LARGE_DOC_THRESHOLD
    const langsInDoc = collectFenceLangs(text)
    const needLangs = isLargeDoc
      ? new Set([...langsInDoc].filter((l) => COMMON_LANGS.has(l)))
      : langsInDoc
    if (needLangs.size > 0) {
      await ensureHLJS()
    }
    // 目录直接由 Markdown 文本构建
    tocItems.value = parseHeadingsFromMd(text)
    const tRenderStart = performance.now()
    guideHtml.value = md.render(text)
    const tRender = performance.now()
    await nextTick()
    const tTick = performance.now()
    console.info(
      '[Guide Perf] fetch:',
      (tFetch - t0).toFixed(1),
      'ms; render:',
      (tRender - tRenderStart).toFixed(1),
      'ms; nextTick:',
      (tTick - tRender).toFixed(1),
      'ms; total:',
      (tTick - t0).toFixed(1),
      'ms'
    )
    // DOM 就绪后校准标题 id（与目录一致）
    ensureHeadingsId()
    enableAnchorScroll()
  } catch (e) {
    guideHtml.value = `<p style="color:#f00">加载失败：${esc(e.message)}</p>`
  } finally {
    guideLoading.value = false
  }
}

// 在模态中启用锚点滚动到标题
const enableAnchorScroll = () => {
  const container = guideContainer.value
  if (!container) return
  container.addEventListener('click', (ev) => {
    const link = ev.target.closest('a')
    if (!link) return
    const href = link.getAttribute('href') || ''
    if (href.startsWith('#')) {
      ev.preventDefault()
      const id = decodeURIComponent(href.slice(1))
      const target = container.querySelector(
        `[id="${
          typeof CSS !== 'undefined' && CSS.escape ? CSS.escape(id) : id
        }"]`
      )
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }
  })

  // 侧栏 TOC 链接也启用平滑滚动
  const sidebar = tocSidebar.value
  if (sidebar) {
    sidebar.addEventListener('click', (ev) => {
      const link = ev.target.closest('a')
      if (!link) return
      const href = link.getAttribute('href') || ''
      if (href.startsWith('#')) {
        ev.preventDefault()
        const id = decodeURIComponent(href.slice(1))
        const target = container.querySelector(
          `[id="${
            typeof CSS !== 'undefined' && CSS.escape ? CSS.escape(id) : id
          }"]`
        )
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
      }
    })
  }
}

// 确保标题 id 与目录一致，并隐藏正文原始 TOC
const ensureHeadingsId = () => {
  const container =
    guideContainer.value ||
    document.querySelector('.ant-modal .markdown') ||
    document.querySelector('.guide-layout .markdown')
  if (!container) return
  const maybeToc = container.querySelector('.toc, .table-of-contents, nav.toc')
  if (maybeToc) maybeToc.style.display = 'none'
  const headings = Array.from(
    container.querySelectorAll('h1, h2, h3, h4, h5, h6')
  )
  let idx = 0
  headings.forEach((h) => {
    const title = (h.textContent || '').replace(/¶\s*$/, '').trim()
    const wantId = slugify(title)
    if (!h.id || h.id !== wantId) h.id = wantId
    if (tocItems.value[idx] && tocItems.value[idx].text === title)
      tocItems.value[idx].id = wantId
    idx++
  })
}

// 模板中使用的 URL 编码方法
const enc = encodeURIComponent
</script>

<style lang="less" scoped>
@import '../styles/color.less';
.main {
  background-color: #f5f7fa;
}
.title {
  background-color: @firstColor;
  color: #fff;

  .menu-item {
    color: #fff;
    border-color: transparent;

    &-active {
      border-color: #ffffff;
    }
  }
}

/* 模态中的两栏布局 */
.guide-layout {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}
.toc-sidebar {
  width: 240px;
  flex: 0 0 240px;
  position: sticky;
  top: 8px;
  align-self: flex-start;
  max-height: calc(100vh - 16px);
  overflow: auto;
  background: #0f172a; /* 暗色背景 */
  border: 1px solid #1f2937;
  border-radius: 8px;
  padding: 12px;
  color: #e5e7eb;
}

/* 简易 Markdown 样式，提升可读性 */
.markdown {
  flex: 1 1 auto;
}

/* 由于内容使用 v-html 注入，使用 :deep 作用到其内部元素 */
:deep(.markdown h1),
:deep(.markdown h2),
:deep(.markdown h3) {
  color: #1f2937;
  margin: 12px 0 8px;
}
:deep(.markdown h1) {
  font-size: 20px;
}
:deep(.markdown h2) {
  font-size: 18px;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 4px;
}
:deep(.markdown h3) {
  font-size: 16px;
}
:deep(.markdown p) {
  margin: 8px 0;
}
:deep(.markdown ul) {
  padding-left: 20px;
}
:deep(.markdown li) {
  margin: 6px 0;
}
/* 使用 hljs 暗色主题，避免覆盖块级代码背景 */
:deep(.markdown code):not(.hljs) {
  background: #f5f7fa;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  padding: 0 4px;
}
:deep(.markdown pre) {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  overflow-x: auto;
  background: transparent;
}

/* 隐藏正文中原位置的 TOC，避免与侧栏重复显示 */
:deep(.markdown .toc),
:deep(.markdown .table-of-contents),
:deep(.markdown nav.toc) {
  display: none !important;
}

/* TOC 样式 */
/* 侧栏内 TOC 列表样式（v-html 内容需使用 :deep） */
:deep(.toc-sidebar ul),
.toc-sidebar .toc-list,
.toc-sidebar .toc-sub {
  list-style: none;
  padding-left: 12px;
  margin: 0;
}
:deep(.toc-sidebar li) {
  margin: 6px 0;
}
:deep(.toc-sidebar a) {
  color: #93c5fd;
  text-decoration: none;
}
:deep(.toc-sidebar a:hover) {
  text-decoration: underline;
  color: #bfdbfe;
}

/* 侧栏空状态 */
.toc-sidebar .empty-toc {
  color: #94a3b8;
  font-size: 12px;
}

/* 表格与任务列表样式 */
:deep(.markdown table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
}
:deep(.markdown th),
:deep(.markdown td) {
  border: 1px solid #e5e7eb;
  padding: 8px;
  text-align: left;
}
:deep(.markdown .task-list-item) {
  list-style: none;
}
:deep(.markdown .task-list-item input) {
  margin-right: 6px;
}

/* 标题锚点样式 */
.header-anchor {
  color: #9ca3af;
  margin-left: 6px;
  text-decoration: none;
}
.header-anchor:hover {
  color: #374151;
}
</style>
