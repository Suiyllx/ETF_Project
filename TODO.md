# ETF 量化平台 · 优化 Todo List

> 最后更新：2026-06-26（E4d 日报邮件卖出信号缺失修复）
> 标注说明：**优先级** 高🔴 / 中🟡 / 低🟢；**范围** 前端`FE` / 后端`BE` / 全栈`FS` / 数据`DATA` / 新模块`NEW`

---

## A · 快速修复（已知待办）

| # | 任务 | 优先级 | 范围 |
|---|------|--------|------|
| A1 | ~~**SignalView Tab 排序**：「卖出信号」移至「今日信号」后~~ ✅ 2026-06-24 完成（随 E2a 一并修复） | 🔴 | FE |

---

## B · 持仓 & 交易页面补齐（第一性原理）

> 核心问题：目前持仓无实时价/浮盈，"总资产"用成本价计算（失真），交易记录与持仓完全独立（双重维护）。

| # | 任务 | 优先级 | 范围 |
|---|------|--------|------|
| B1 | ~~**持仓明细增加实时价 / 浮盈浮亏**：新增「现价」「现值」「浮盈」「浮盈%」列，调用已有 `/api/realtime-price`；顶部「持仓估值」改用市价，新增「总浮盈」卡片~~ ✅ 2026-06-24 完成 | 🔴 | FS |
| B1a | ~~**持仓行卖出信号角标**：PortfolioView 切换账户时并发拉取 `/api/sell-signals`，ETF 名称旁显示「止损/止盈/看空」彩色 badge~~ ✅ 2026-06-24 完成 | 🔴 | FE |
| B1b | ~~**快速加仓/减持**：操作列新增 +加仓 / -减持 按钮，点击在行内展开气泡表单（股数+价格+预览扣款/到账），确认后调用 `POST /api/transactions` 同时更新持仓+现金~~ ✅ 2026-06-24 完成 | 🔴 | FE |
| B2 | ~~**交易→持仓自动联动**：新增交易时自动更新持仓股数 & 加权均成本，卖出自动减仓，现金余额同步增减~~ ✅ 后端 `api_create_transaction` 已实现，B1b 提供前端快捷入口 | 🔴 | BE |
| B3 | **已实现盈亏追踪**：卖出交易自动计算实现盈亏（卖价 − 加权均成本 × 股数），交易列表新增「实现盈亏」列，顶部增加「累计实现盈亏」汇总卡片 | 🟡 | FS |
| B4 | **持仓仓位可视化**：每行显示仓位权重（% + 迷你进度条）；持仓 Tab 侧边/顶部加板块分布饼图（宽基 / 行业 / 债券 / 商品） | 🟡 | FE |
| B5 | **交易记录筛选 & 汇总**：加日期范围 + ETF 名称筛选框；底部显示期间买入/卖出总金额、交易笔数、实现盈亏汇总行 | 🟡 | FE |
| B6 | **资产走势图**：每日收盘后快照各用户总资产，持仓页新增「收益曲线」Tab，折线图对比多用户及沪深300基准 | 🟢 | FS |

---

## C · ETF 票池扩充

> 当前 28 只，缺少银行、AI/机器人、消费细分、化工、石油等主流行业。

| # | 任务 | 优先级 | 范围 |
|---|------|--------|------|
| C1 | ~~**补充主流 ETF（26 → 61 只）**：新增 35 只，覆盖银行/保险/AI/机器人/家电/食品饮料/化工/石油/创新药/医疗器械/北证50/中证2000/中概互联/纳斯达克100/恒生科技/标普500/储能/电力/碳中和/云计算/网络安全/钢铁/农业/传媒/5G/央企改革/环保/基建/30年国债/可转债/白银/豆粕 等~~ ✅ 2026-06-24 完成 | 🟡 | DATA |
| C2 | ~~**ETF 分类体系细化**：category 从 4 类细化为 11 类（宽基/海外/金融/医疗/科技/能源/消费/周期/地产/债券/商品），`/api/etf-list` 返回 names+categories，`store.etfCategories` 全局可用；行情页侧栏按板块折叠分组（▼/▶ 一键展收），信号页顶部分类筛选条~~ ✅ 2026-06-24 完成 | 🟡 | FS |
| C3 | ~~**新 ETF 补拉历史数据 & 模型更新**：`fetch_historical --skip-existing --years 3` 补拉 35 只（全部成功），重训练 `lgbm_forward5_20260624.pkl`（数据集 18876→39719 行，2.1×），信号覆盖量 26→61 只（12 只 prob_up≥0.5）~~ ✅ 2026-06-24 完成 | 🟢 | DATA |
| C4 | ~~**ETF 票池代码↔名称全量纠错**：逐只核对 61 只代码与真实基金名称/分类，修复 11 处错配（环保→稀土、北证50/白银实为黄金、地产实为科技龙头、军工实为基建、159806↔159869 网络安全/新能源车实为新能源车/动漫游戏对调、石油/碳中和/储能 3 只代码完全对不上主题改用真实代码 561360/159790/159566），补拉新代码历史数据，重训 `lgbm_forward5_20260626.pkl`~~ ✅ 2026-06-26 完成 | 🔴 | DATA |

---

## D · 个股模块（全新功能）

> 在 ETF 体系外，新增对用户自选 A 股个股的投资机会挖掘。

| # | 任务 | 优先级 | 范围 |
|---|------|--------|------|
| D1 | **架构设计**：确定股票池管理方案（用户自选 + 预设行业龙头池）、数据源（Tushare pro_bar）、特征工程与 ETF 差异（涨跌停/停牌/财报季处理）、与现有 ETF 流水线的共用与隔离边界 | 🔴 | NEW |
| D2 | **个股历史数据拉取**：新建 `quant/data/fetch_stocks.py`，Tushare `pro_bar` 拉取 A 股日线，处理停牌/复权，存 `quant/data/historical/stocks/` parquet | 🟡 | DATA |
| D3 | **个股特征工程 & 信号生成**：新建 `quant/signals/stock_generator.py`；在技术指标基础上增加换手率、量比、相对大盘强弱、N 日成交量异动等特征；单独训练个股分类模型；输出 `stock_candidates.json` | 🟡 | NEW |
| D4 | **前端个股看板 StockView.vue**：导航栏新增「个股」Tab（所有用户可见）；含：我的股票池管理（增/删/搜索）、今日个股信号列表、实时报价 | 🟡 | FE |
| D5 | **持仓 / 交易兼容个股**：持仓表格新增「类型」列（ETF / 个股）；新增交易弹窗搜索同时覆盖股票；卖出信号联动支持个股 | 🟢 | FS |

---

## E · 项目架构优化

> 随着功能增长，当前单文件后端 + 超大 Vue 文件的结构会成为维护瓶颈。

### E1 · 后端拆分（web_app.py → Flask Blueprints）

`web_app.py` 当前 951 行，所有 API 混在一起。建议按资源拆蓝图：

```
web_app.py          # 只保留 app 初始化、配置、静态文件服务
routes/
  auth.py           # /api/auth/*
  portfolio.py      # /api/portfolio/* /api/transactions/*
  signals.py        # /api/signals /api/sell-signals /api/alerts /api/signal-history
  admin.py          # /api/model-config /api/backtest /api/email-log /api/system-status
  market.py         # /api/realtime-price /api/etf-list /api/paper-trades
```

| # | 任务 | 优先级 | 范围 |
|---|------|--------|------|
| E1 | ~~**web_app.py 拆分为 Flask Blueprints**，按上述结构分文件，不改变任何 API 行为~~ ✅ 2026-06-24 完成 | 🟡 | BE |

### E2 · 前端组件拆分

三个主视图文件均超过 800 行，逻辑与模板混杂：

| # | 任务 | 优先级 | 范围 |
|---|------|--------|------|
| E2a | ~~**SignalView.vue 拆子组件**：`TodaySignalTab.vue`、`SellSignalTab.vue`、`PaperTradeTab.vue`~~ ✅ 2026-06-24 完成（931→320 行，含 A1 Tab 顺序修复） | 🟡 | FE |
| E2b | ~~**PortfolioView.vue 拆子组件**：`PositionTab.vue`、`TransactionTab.vue`~~ ✅ 2026-06-24 完成（950→280 行） | 🟡 | FE |
| E2c | **EtfView.vue 拆子组件**：930 行，Canvas Chart 状态耦合紧，暂缓 | 🟢 | FE |

### E3 · 数据层改造

| # | 任务 | 优先级 | 范围 |
|---|------|--------|------|
| E3 | **JSON 文件 → SQLite**：`users.json` / `{user_id}.json` / `transactions` 迁移到单个 `portfolios.db`，用 Python 内置 `sqlite3`；解决并发读写无锁的隐患，并支持交易记录分页查询 | 🟢 | BE |

### E4 · 量化流水线健壮性

| # | 任务 | 优先级 | 范围 |
|---|------|--------|------|
| E4a | ~~**日任务错误恢复**：`run_daily.py` 各阶段（数据拉取→特征→信号→邮件）加独立 try/except + 失败重试（指数退避），任意环节失败不阻断后续，并写入结构化日志~~ ✅ 2026-06-24 完成 | 🟡 | BE |
| E4b | ~~**模型版本管理**：训练后保存 `model_{date}.pkl`，`model_config.json` 记录当前激活版本；支持从 ModelView 一键回滚到前一个版本~~ ✅ 2026-06-24 完成 | 🟢 | BE |
| E4c | ~~**Tushare 调用封装**：将所有 Tushare 调用统一到 `quant/data/tushare_client.py`，加请求频率限制（Tushare Pro 有调用次数限制）和超时重试，防止因网络抖动导致数据缺失~~ ✅ 2026-06-24 完成 | 🟡 | BE |
| E4d | ~~**日报邮件缺失卖出信号修复**：`run_daily.py` 生成卖出信号后结果被丢弃（`_, ok = run_with_retry(...)`），且 `notifier.py` 日报 HTML 模板本身没有卖出信号区块；现已按用户传入 `push_daily_report`，邮件新增「🔴 卖出提醒」表格（止损/止盈/模型看空 + 浮盈亏 + 触发说明）~~ ✅ 2026-06-26 完成 | 🔴 | BE |

---

## F · 前端视觉重构（Apple 风格 · 深色优先 + 毛玻璃）

> 设计方向已通过 `design_preview.html` 静态预览确认：参考 Apple 股市 App 的视觉语言——深色为默认主题（支持浅色切换）、卡片用半透明毛玻璃（`backdrop-filter: blur` + 柔和投影）、系统蓝/绿/红/橙做语义色、苹方/SF 系统字体、大字号轻量数字、胶囊按钮、分段控件（Segmented Control）、sparkline 迷你走势线。
>
> 现状调研结论：`tailwind.config.js` 无任何 theme 扩展，颜色全部写死在 inline style 里；`store.js` 无主题状态；8 个视图/组件样式重复率 60%+，无基础组件库。因此重构必须先搭基础设施，再铺组件，最后逐页迁移，避免每页各做一套。

| # | 任务 | 优先级 | 范围 |
|---|------|--------|------|
| F1 | ~~**设计基础设施**：`tailwind.config.js` 新增 `darkMode: 'class'` + 扩展色板 token（系统蓝 `#0a84ff`/`#007aff`、绿 `#30d158`/`#34c759`、红 `#ff453a`/`#ff3b30`、橙 `#ff9f0a`/`#ff9500`，深浅两套）；`style.css` 新增 CSS 变量（`--glass-bg`/`--glass-border`/`--glass-shadow`/`--surface-1/2/3`/`--label-1/2/3`），深浅模式各一套~~ ✅ 2026-06-26 完成（`:root` 深色默认，`html.light` 浅色覆盖，与 `design_preview.html` 一致） | 🔴 | FE |
| F2 | ~~**主题状态管理**：`store.js` 新增 `darkMode`（默认深色）+ `localStorage` 持久化；提供 `toggleDarkMode()`，挂载时同步 `document.documentElement.classList`~~ ✅ 2026-06-26 完成（`localStorage` key `etf-theme`，模块加载时立即同步避免闪屏；UI 切换按钮留给 F4） | 🔴 | FE |
| F3 | ~~**基础组件库**：新建 `components/base/` 目录，产出 5 个通用组件——`BaseCard.vue`（毛玻璃卡片）、`BaseButton.vue`（胶囊按钮，primary/green/red/danger/ghost 变体）、`SegmentControl.vue`（分段控件，替换现有 Tab 按钮组）、`StatCard.vue`（大字号统计卡片，支持涨跌色 + sparkline）、`Badge.vue`（语义化标签，内置买入建议/卖出触发两套映射）~~ ✅ 2026-06-26 完成（补充 `--sys-*-dim` 淡色背景 token 到 F1 的 style.css/tailwind.config.js） | 🔴 | FE |
| F4 | ~~**App.vue 全局外壳改造**：顶部导航栏 + 侧边栏迁移到毛玻璃风格（`backdrop-filter` + 半透明背景），新增深浅色切换按钮（沿用 `design_preview.html` 的 🌙/☀️ 交互）~~ ✅ 2026-06-26 完成 | 🟡 | FE |
| F5 | ~~**信号看板改造**（SignalView + 子组件）：组件迁移到 `BaseCard`/`Badge`/`StatCard`/`SegmentControl`；**布局重构**：原 5 个 Tab（今日信号/卖出信号/历史档案/模拟盘胜率/算法说明）精简为 2 个 Tab——「信号」（卖出提醒在上+今日买入信号在下，堆叠布局）、「模拟盘胜率」；历史档案改为右上角按钮触发的右侧滑出抽屉（主从布局：左侧日期列表+右侧信号详情）；算法说明改为「？」帮助弹窗~~ ✅ 2026-06-26 完成（已登录实测全部交互：Tab 切换、历史抽屉、帮助弹窗，深色玻璃主题渲染正常） | 🟡 | FE |
| F5a | ~~**配色淡化 + 毛玻璃补全**：`SignalCard`/`SellSignalTab` 头部和 ETF 代码方块原来用纯色块（`bg-sys-green` 等）太刺眼，改成 dim 背景+同色文字；根本问题是主内容区背景是纯色 `bg-bg`，毛玻璃卡片背后没有色彩可模糊——新增 `.app-bg` 工具类（`style.css` 内三个低饱和度光斑 + `background-attachment:fixed`），挂到 `App.vue` 的 `<main>`，所有已迁移页面自动获得真实毛玻璃效果~~ ✅ 2026-06-26 完成 | 🔴 | FE |
| F5b | ~~**图标体系替换**：emoji 图标（📡💼📈🔔⚡ 等）与玻璃质感风格不搭，改用 `@lucide/vue`（细线条图标库，已安装为依赖）；替换范围：`App.vue` 侧栏导航 7 个图标 + Logo + 深浅色切换、`SignalView` 历史/帮助按钮 + 弹窗标题、`SellSignalTab`/`TodaySignalTab`/`PaperTradeTab` 的按钮图标和空状态大图标、`SignalCard` 的建议说明图标和操作按钮~~ ✅ 2026-06-26 完成（之后新增页面统一用 `@lucide/vue`，不要再引入 emoji 作为 UI 图标） | 🟡 | FE |
| F6 | ~~**持仓管理改造**（PortfolioView + 子组件）：顶部汇总卡片迁移到 `StatCard`（现金卡叠加「+入金」按钮）；用户头部横幅改玻璃卡片（去掉纯色渐变 banner）；Tab 改 `SegmentControl`；`PositionTab`/`TransactionTab` 表格行+徽章+弹窗全部迁移到新 token 和 `Badge`/`BaseCard`/`BaseButton`；`EtfSearch` 下拉框同步迁移；图标用 `@lucide/vue`~~ ✅ 2026-06-28 完成（已登录实测三个 Tab + 加仓/减持/导入持仓/入金四个弹窗交互） | 🟡 | FE |
| F7 | ~~**ETF 行情页改造**（EtfView，893 行最大文件）：侧栏分类列表+搜索结果行+空状态/加载态迁移到新 token；详情头部卡片、控制栏、图表卡片、指标说明面板全部迁移到 `BaseCard`/`Badge`；Chart.js 网格线透明度调低适配深色背景；图标用 `@lucide/vue`~~ ✅ 2026-06-28 完成（未拆子组件，文件体量未变，留作后续技术债） | 🟢 | FE |
| F8 | ~~**管理员页面改造**（ModelView / BacktestView / EmailView / SystemView）：`ModelView`（736 行，纯自定义 CSS 非 Tailwind）把全部色值换成 CSS 变量并补毛玻璃，4 个 section（候选池/盘中阈值/回望周期/模型版本）+ 滑杆/黑名单/版本管理全部适配；其余 3 个页面迁移到 `BaseCard`/`StatCard`/`Badge`；图标用 `@lucide/vue`~~ ✅ 2026-06-28 完成 | 🟢 | FE |
| F9 | ~~**登录页改造**（LoginView）：品牌感欢迎页，毛玻璃登录卡片 + 渐变光斑背景（复用 `design_preview.html` 的背景光斑方案）；图标用 `@lucide/vue`~~ ✅ 2026-06-28 完成（F 系列全部完成） | 🟢 | FE |

---

## G · 信号质量优化

> 起因：2026-06-29 发现买入信号池子里混入不少明显处于下降趋势的 ETF（如钢铁ETF连续推荐但价格持续创新低）。用历史信号回测发现样本太少（仅14条有完整5日后验结果）无法判断 MA20 等趋势过滤的有效性，但发现煤炭ETF（515220）连续5天被推荐、动量持续恶化、5天后全部亏损，说明问题不在"票池太大"而在"同一标的连续误判未被抑制"。

| # | 任务 | 优先级 | 范围 |
|---|------|--------|------|
| G1 | ~~**历史信号回测工具**：新建 `quant/signals/backtest_history.py`，读取 `quant/signals/history/*.json` + `quant/data/historical/*.parquet`，计算每条历史信号的真实 forward 收益/胜率，支持 `--group-by` 按指标正负分组对比，`--min-samples` 样本不足时提示结论不可靠~~ ✅ 2026-06-29 完成（用法：`python -m quant.signals.backtest_history --group-by ma_dev_20`；当前仅14条完整样本，57.1%胜率，暂不足以验证趋势过滤假设） | 🔴 | DATA |
| G2 | **连续失效信号降权**：信号生成时检测同一 ETF 是否连续 N 天（如 ≥3）被推荐但 `mom_20`/价格持续恶化，达到条件则降权或从候选池剔除当日信号，避免重复推荐同一个正在下跌的标的 | 🟡 | BE |

---

## 优先级汇总

```
立即可做（小改动）  ：B3, B4, B5
中期推进（中等工作量）：C1, C2, D1
长期规划（大功能/重构）：B6, C3, D2, D3, D4, D5, E2c, E3

前端视觉重构（F1→F9 全部完成 ✅ 2026-06-28）：Apple 风格深色玻璃主题已覆盖全部页面，
  新页面/新组件请直接复用 components/base/ 五件套 + style.css 的 token，不要再引入硬编码颜色或 emoji 图标。

已完成：A1 ✅  B1 ✅  B1a ✅  B1b ✅  B2 ✅  C1 ✅  C2 ✅  C3 ✅  C4 ✅  E1 ✅  E2a ✅  E2b ✅  E4a ✅  E4b ✅  E4c ✅  E4d ✅  F1 ✅  F2 ✅  F3 ✅  F4 ✅  F5 ✅  F5a ✅  F5b ✅  F6 ✅  F7 ✅  F8 ✅  F9 ✅（前端视觉重构全部完成）
```

---

*本文件与 CLAUDE.md 配套维护，完成项后在对应行前加 `[x]` 或删除条目。*
