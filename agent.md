# not-book Agent 指南

> 本文件供 AI Agent（如 Trae IDE 中的 Agent）阅读，用于理解项目架构、开发规范和可用工具，以便高效协作开发。

## 项目概览

| 项目 | 说明 |
|---|---|
| 名称 | not-book · AI 长篇创作工作台 |
| 定位 | 基于 AI 的长篇小说创作工具，不是聊天框，是完整的项目工作台 |
| 仓库 | https://github.com/hxhming/not-book |
| 技术栈 | Vue 3 (Composition API) + Element Plus + Font Awesome 6，纯前端单文件 SPA |
| 入口文件 | `/workspace/index.html`（所有 HTML/CSS/JS 内联，无构建步骤） |
| 后端 | `/workspace/not_book/`（Django，含 `task` app），数据库 `db.sqlite3` |
| 管理后台 | `/workspace/admin/index.html`、`/workspace/admin/login.html` |

## 技术栈详情

- **Vue 3**：CDN 引入 `vue.global.prod.js`，使用 `createApp` + `setup()` Composition API
- **Element Plus**：CDN 引入，含 `@element-plus/icons-vue` 全量注册
- **Font Awesome 6.2.0**：图标库
- **存储**：纯浏览器 `localStorage`（云端存储为占位，提示"开发中"）
- **AI 接入**：兼容 OpenAI Function Calling 协议的多家服务商（9 家 provider）

## 整体架构

```
index.html
├── <style>          (line 14-1738)    CSS：三套主题 + 全部组件样式
├── <div id="app">   (line 1743-4035)  Vue 模板
│   ├── Home          (line 1743-1880)  Landing 页
│   └── Workshop      (line 1883-3588)  工作台
│       ├── Projects  (line 2058-2111)  项目列表
│       ├── Tasks     (line 2114-2202)  任务管理
│       ├── Editor    (line 2205-3397)  编辑器（11 个子模块）
│       └── Settings  (line 3400-3585)  设置（4 个 Tab）
├── 12 个 el-dialog  (line 3590-4035)  弹窗
└── <script>         (line 4042-7018)  Vue 应用逻辑
    ├── setup()      (line 4044-6936)  所有响应式数据 + 函数
    ├── watch        (line 6876-6920)  自动保存监听
    └── app.mount    (line 7018)       挂载
```

## 视图层级

```
view: 'home' | 'workshop'
├── home: Landing 页（功能介绍 / 技术栈 / 关于）
└── workshop:
    ├── wsPage: 'projects' | 'tasks' | 'editor' | 'settings'
    │   ├── projects: 项目列表 + 创建新项目
    │   ├── tasks: 任务管理（CRUD + 筛选）
    │   ├── editor (需 currentNovel):
    │   │   └── editorSection: 11 个子模块
    │   │       ├── outline       书名与核心设定
    │   │       ├── synopsis      故事大纲（卷-章）
    │   │       ├── fate-line     命运线（驱动编辑器章节树）
    │   │       ├── perspectives  上帝视角图
    │   │       ├── characters    人物与关系（6 个 Tab）
    │   │       ├── world         世界观设定（嵌套分组）
    │   │       ├── plotlines     剧情线
    │   │       ├── promises      伏笔 / 承诺台账
    │   │       ├── editor        AI 续写编辑器
    │   │       ├── tools         作家工具
    │   │       ├── ai            AI 助手
    │   │       └── ai-cache      AI 缓存
    │   └── settings:
    │       └── settingsTab: 'profile' | 'preferences' | 'ai' | 'tools'
```

## 数据存储

### LocalStorage Key 命名规则

**全局 key**（不带项目 ID）：

| Key | 说明 |
|---|---|
| `nb_novels` | 小说列表 |
| `nb_tasks` | 任务列表 |
| `nb_aimodels` | AI 模型配置列表 |
| `nb_theme` | 主题（dark/light/pure-black） |
| `userLoggedIn` | 登录状态（`'1'`） |
| `userUsername` | 当前用户名 |
| `users` | 用户列表 |
| `nb_view` / `nb_wsPage` / `nb_editorSection` / `nb_currentNovelId` | 界面状态 |

**按项目 ID 隔离的 key**（格式 `nb_<key>_<novelId>`）：

| Key | 说明 |
|---|---|
| `nb_chapters_<id>` | 章节数组 |
| `nb_characters_<id>` | 角色数组 |
| `nb_synopsisVolumes_<id>` | 大纲卷数组 |
| `nb_foreshadows_<id>` | 伏笔数组 |
| `nb_plotlines_<id>` | 剧情线数组 |
| `nb_worldCategories_<id>` | 世界观分组树 |
| `nb_worldSettings_<id>` | 世界观内容项 |
| `nb_history_<id>` | 历史版本（最多 50 条） |
| `nb_fate_<id>` | 命运线 `{ volumes, currentVolId, currentChId }` |

### 通用存取函数

```javascript
// 保存数据（按项目 ID 隔离）
function saveNovelData(key, data) {
  localStorage.setItem('nb_' + key + '_' + currentNovel.value.id, JSON.stringify(data));
}

// 加载数据
function loadNovelData(key, defaultValue) {
  const data = localStorage.getItem('nb_' + key + '_' + currentNovel.value.id);
  return data ? JSON.parse(data) : defaultValue;
}

// 一次性保存所有核心数据
function autoSaveAll() { ... }

// 自动保存监听（watch + deep: true）
watch(characters, (val) => saveNovelData('characters', val), { deep: true });
// ... 对 chapters/synopsisVolumes/foreshadows/plotlines/worldCategories/worldSettings 同理
```

## 核心数据结构

### novel（小说项目）

```javascript
{
  id: number,              // 自增 ID
  title: string,           // 作品名称
  category: string,        // 分类
  description: string,     // 一句话简介
  chapterCount: number,    // 章节数
  wordCount: number,       // 总字数
  targetWords: number,     // 目标字数（5万-500万）
}
```

### character（角色）

```javascript
{
  id: number,
  name: string,
  role: string,            // 身份
  age: string,
  gender: 'male' | 'female' | 'other',
  color: string,           // 头像渐变色
  personality: string,     // 性格
  appearance: string,      // 外貌
  background: string,      // 背景
  catchphrase: string,     // 口头禅
  hobbies: string,         // 爱好
  weakness: string,        // 弱点
  relations: [{ targetId, targetName, relationType, description, source: 'manual'|'ai', createdAt }],
  arcs: [{ stage, title, description, volume, chapter, source, createdAt }],
  experiences: [{ title, description, volume, chapter, source, createdAt }],
  memories: [{ content, volume, chapter, importance: 'high'|'medium'|'low', source, createdAt }],
  attributes: [{ name, value }],  // 自定义属性
}
```

### chapter（章节）

```javascript
{
  id: number,
  title: string,    // "第一章 孤身赴边"
  content: string,  // 正文
}
```

### synopsisVolume（大纲卷）

```javascript
{
  title: string,
  summary: string,
  plots: [{ content }],
  chapters: [{ title, summary }],
}
```

### fateVolume（命运线卷）

```javascript
{
  id: number,
  title: string,
  chapterIds: number[],  // 引用 chapters[].id
}
```

### worldCategory（世界观分组）

```javascript
{
  id: string,             // 'geography' | 'group_<timestamp>' | 'subgroup_<timestamp>'
  name: string,
  icon: string,           // FontAwesome 类名
  content: string,
  children: worldCategory[],  // 子分组（支持嵌套）
  expanded: boolean,
  parentId?: string,      // 子分组才有
}
```

### worldSettings（世界观内容项）

```javascript
// 按分组 ID 索引的字典
{
  [catId]: [{ id, name, content, _editing?: boolean }]
}
```

### plotline（剧情线）

```javascript
{
  id: number,
  name: string,
  color: string,
  description: string,
  nodes: [{ title, description, volume, chapter, source, createdAt }],
}
```

### foreshadow（伏笔/承诺）

```javascript
{
  title: string,
  description: string,
  setupVolume: number | null,
  setupChapter: number | null,
  payoffVolume: number | null,
  payoffChapter: number | null,
  importance: 'high' | 'medium' | 'low',
  status: 'unresolved' | 'resolved',
  source: 'manual' | 'ai',
  createdAt: string,
}
```

### perspective（上帝视角）

```javascript
{
  id: string,
  name: string,
  description: string,
  characterIds: number[],
  timeline: [{ time, title, description }],
}
```

### historyVersion（历史快照）

```javascript
{
  id: number,         // Date.now()
  timestamp: string,  // 本地化时间
  data: {
    characters, worldCategories, worldSettings,
    synopsisVolumes, plotlines, foreshadows, chapters
  }
}
```

### aiModel（AI 模型配置）

```javascript
{
  id: number,
  name: string,
  providerType: 'openai'|'anthropic'|'deepseek'|'moonshot'|'baidu'|'alibaba'|'tencent'|'zhipu'|'custom',
  provider: string,
  baseUrl: string,
  apiKey: string,
  modelName: string,
  supportsText: boolean,
  supportsVector: boolean,
  supportsImage: boolean,
  useCase: 'primary'|'assistant'|'vector_only'|'image_only',
  isDefault: boolean,
}
```

## AI 工具系统（Function Calling）

### 可用工具

| 工具名 | 类型 | 功能 | 关键参数 |
|---|---|---|---|
| `list_characters` | 只读 | 列出所有角色 | `role_filter` |
| `get_character_info` | 只读 | 查询角色详情 | `character_id`/`character_name`, `info_type`, `volume`, `chapter` |
| `get_world_setting` | 只读 | 获取世界观设定 | `category`: all/geography/history/... |
| `get_synopsis` | 只读 | 获取故事大纲 | `volume`, `include_chapters` |
| `get_foreshadows` | 只读 | 获取伏笔列表 | `status`, `importance` |
| `get_plotlines` | 只读 | 获取剧情线节点 | `plotline_id`, `up_to_volume` |
| `get_chapter_content` | 只读 | 获取章节正文 | `chapter_id` 或 `volume`+`chapter_num` |
| `add_character_memory` | **写入** | 给角色添加记忆 | `character_id`, `content`, `volume`, `chapter`, `importance` |
| `add_foreshadow` | **写入** | 新增伏笔 | `title`, `description`, `setup_volume`, `setup_chapter`, `importance` |

### 权限控制

```
Ask 模式：只能调用 7 个只读工具
Agent 模式 + 需确认：调用写工具前弹出确认框，用户同意后才执行
Agent 模式 + 直接执行：AI 拥有所有权，直接执行
```

### 工具调用流程

```
用户输入 → detectToolIntent(关键词匹配) → isToolAllowed(权限过滤) → executeTool → formatQueryResults(渲染)
```

## AI 功能模块

### 编辑器续写模式

- 双输入框：`editorPromptInput`（提示词）+ `editorNovelInput`（小说内容）
- 三态切换：`both` / `prompt` / `novel`
- AI 消息结构：思考内容（折叠）→ 正文 → 总结（折叠）
- **回溯功能**：每条 AI 消息有回溯按钮，点击后移除该次及之后所有 AI 生成内容

### AI 助手

- Ask/Agent 模式切换
- Agent 权限控制：需确认 / 直接执行
- 快捷操作按钮（Ask 5 个查询 + Agent 6 个生成）
- 工具调用结果渲染

## 命运线与大纲的关系

- `fateVolumes` 是真正驱动编辑器章节树的来源
- `synopsisVolumes` 是大纲规划层
- 打开小说时若 `fateVolumes` 为空会自动从 `synopsisVolumes` 迁移
- `editorSection` 切到 `synopsis` 时会同步命运线当前卷到大纲

## 主题系统

三套主题通过 `data-theme` 属性切换：

| 主题 | data-theme | 背景色 | 主色 |
|---|---|---|---|
| dark（默认） | 无 | `#0a0a12` | `#8b5cf6`（紫） |
| light | `light` | `#ffffff` | `#8b5cf6` |
| pure-black (OLED) | `pure-black` | `#000000` | `#8b5cf6` |

CSS 变量：`--primary` / `--bg-primary` / `--bg-card` / `--text-primary` / `--border-color` 等。

## 响应式设计

`@media (max-width: 768px)` 时：
- 侧边栏缩至 60px，隐藏文字
- 统计卡改 2 列
- 设置页改纵向布局
- 编辑器隐藏左右栏，调整高度

## 开发注意事项

1. **单文件架构**：所有代码在 `index.html` 中，修改时注意行号会偏移
2. **响应式数据**：所有数据用 `ref` / `reactive`，通过 `watch + deep: true` 自动保存
3. **项目隔离**：数据按 `novelId` 隔离存储，切换项目时需重新加载
4. **计算属性顺序**：computed 属性不能依赖在其之后才定义的变量，否则初始化崩溃
5. **AI 模拟**：除 `fetchModelsFromApi` 真实调用 API 外，其余 AI 生成均为 mock
6. **字数计算**：统一使用 `content.length`（字符数），非真实中文字数
7. **章节索引**：`get_chapter_content` 使用 `(volume-1)*10 + (chapter_num-1)` 简化算法
8. **测试文件**：`simplified.html` / `test_*.html` 为测试文件，不属于正式代码

## 默认数据

- 2 本示例小说（古代言情《将门孤女》、竞技《投篮轨迹预知者》）
- 4 条示例任务
- 4 章示例正文（沈砚/雁门关题材）
- 3 个用户（hxhming/zhangsan/zhaoliu，测试账号 zhaoliu/zl123456）
- 8 个世界观默认分类（地理/历史/文化/力量/政治/经济/宗教/科技）
- 3 个默认视角（主线/沈砚/萧景琰）

## 关键函数索引

| 函数 | 作用 |
|---|---|
| `saveNovelData(key, data)` | 按项目 ID 保存数据到 LocalStorage |
| `loadNovelData(key, defaultValue)` | 从 LocalStorage 加载数据 |
| `autoSaveAll()` | 一次性保存所有核心数据 |
| `saveChaptersLocal()` | 保存章节数据 |
| `openNovel(novel)` | 打开项目，加载所有相关数据 |
| `manualSave()` | 创建历史快照 |
| `restoreHistoryVersion(version)` | 回溯到历史版本 |
| `executeTool(name, args)` | 执行 AI 工具调用 |
| `sendAi()` | 发送 AI 助手消息 |
| `sendEditorChat()` | 发送编辑器续写消息 |
| `rollbackEditorChat(aiMsgIndex)` | 回溯编辑器 AI 生成内容 |
| `detectToolIntent(content)` | 关键词匹配推断工具 |
| `isToolAllowed(toolName)` | 权限检查 |
| `processAiMessage(content)` | 处理 AI 消息（工具调用+回复） |
