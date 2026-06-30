# ETF 量化管理平台 · 后端 API 文档

> 版本：v1.9（2026-06-30）  
> 基础地址：`http://localhost:8888`（本地）  
> 所有接口均返回 JSON，Content-Type: `application/json`

---

## 认证说明

平台使用 **Session Cookie** 认证。登录后服务端写入 `session["user_id"]`，后续请求携带 Cookie 即可。

| 装饰器 | 含义 |
|---|---|
| `@require_auth` | 必须已登录，未登录返回 `401` |
| `@require_admin` | 必须是管理员（`role == "admin"`），非管理员返回 `403` |

---

## 一、认证

### `POST /api/auth/login`

登录。

**请求体**
```json
{ "username": "suiy", "password": "xxx" }
```

**成功响应 200**
```json
{ "id": "suiy", "name": "Suiy", "role": "admin", "email": "xxx@gmail.com" }
```

**失败响应 401**
```json
{ "error": "用户名或密码错误" }
```

---

### `POST /api/auth/logout`

登出，清除 session。无请求体，成功返回 `204 No Content`。

---

### `GET /api/auth/me`

获取当前登录用户信息。

**成功响应 200**
```json
{ "id": "suiy", "name": "Suiy", "role": "admin", "email": "xxx@gmail.com" }
```

**未登录响应 401**
```json
{ "error": "未登录" }
```

---

### `POST /api/auth/change-password` 🔒

修改当前用户密码。

**请求体**
```json
{ "old_password": "原密码", "new_password": "新密码" }
```

新密码至少 4 位，原密码错误返回 `400`。

---

## 二、用户管理

### `GET /api/users` 🔒

获取用户列表。管理员返回全部用户，普通用户只返回自己。

**响应 200**
```json
[
  { "id": "suiy", "name": "Suiy", "role": "admin", "email": "xxx@gmail.com", "active": true },
  { "id": "alice", "name": "Alice", "role": "user", "email": "", "active": true }
]
```

---

### `POST /api/users` 🔒🛡️

创建新用户（管理员）。默认密码为 `gaoqian`，初始现金和仓位上限可指定。

**请求体**
```json
{
  "name": "alice",
  "email": "alice@example.com",
  "cash": 200000,
  "max_position_pct": 0.30,
  "max_sector_pct": 0.50,
  "active": true
}
```

**响应 201**：返回新创建的用户对象（同 GET /api/users 格式）。

---

### `PUT /api/users/<user_id>` 🔒

更新用户信息。管理员可改所有用户，普通用户只能改自己。可更新字段：`name`、`email`、`active`。

---

### `DELETE /api/users/<user_id>` 🔒🛡️

删除用户（管理员）。同时删除其 portfolio 文件。成功返回 `204`。

---

### `POST /api/users/<user_id>/reset-password` 🔒🛡️

重置指定用户密码（管理员）。

**请求体**
```json
{ "password": "新密码" }
```

不传 `password` 时默认重置为 `user_id`。

---

## 三、持仓

### `GET /api/portfolio/<user_id>` 🔒

获取用户持仓数据（普通用户只能读自己的）。

**响应 200**
```json
{
  "cash": 50000.00,
  "max_position_pct": 0.30,
  "max_sector_pct": 0.50,
  "watchlist": ["512100", "510300"],
  "positions": [
    {
      "code": "515220",
      "name": "煤炭ETF",
      "shares": 10000,
      "cost_price": 1.234,
      "buy_date": "2026-06-01"
    }
  ]
}
```

---

### `PUT /api/portfolio/<user_id>` 🔒

更新持仓基础配置（现金 / 仓位上限）。传哪个字段改哪个，不影响 positions。

**请求体**
```json
{ "cash": 80000, "max_position_pct": 0.25, "max_sector_pct": 0.50 }
```

---

### `POST /api/portfolio/<user_id>/positions` 🔒

导入初始持仓（不扣现金 → 用于导入平台使用前的已有仓位）。若该代码已存在，则合并加权平均成本。

**请求体**
```json
{
  "code": "515220",
  "name": "煤炭ETF",
  "shares": 10000,
  "cost_price": 1.234,
  "buy_date": "2026-06-01"
}
```

> ⚠️ 此接口**不扣减现金**，日常买卖请使用 `POST /api/transactions/<user_id>`。

---

### `DELETE /api/portfolio/<user_id>/positions/<code>` 🔒

直接删除持仓记录（不影响现金）。成功返回 `204`。

---

## 四、自选列表

### `GET /api/watchlist` 🔒

获取当前用户自选 ETF 列表（代码数组）。

**响应 200**
```json
["512100", "510300", "515220"]
```

---

### `PUT /api/watchlist` 🔒

覆盖当前用户自选列表。

**请求体**
```json
["512100", "510300"]
```

---

## 五、交易记录

### `GET /api/transactions/<user_id>` 🔒

获取用户交易记录（倒序，最新在前）。

**响应 200**
```json
[
  {
    "id": "tx_20260630_143022_123456",
    "date": "2026-06-30",
    "action": "buy",
    "etf_code": "515220",
    "etf_name": "煤炭ETF",
    "shares": 5000,
    "price": 1.250,
    "amount": 6250.00,
    "note": "按信号建仓",
    "created_at": "2026-06-30 14:30:22"
  }
]
```

---

### `POST /api/transactions/<user_id>` 🔒

新增交易记录，**自动联动持仓和现金**：

- `action = "buy"`：扣减现金，新建或加仓（加权平均成本）
- `action = "sell"`：增加现金，减仓或清仓

**请求体**
```json
{
  "date": "2026-06-30",
  "action": "buy",
  "etf_code": "515220",
  "etf_name": "煤炭ETF",
  "shares": 5000,
  "price": 1.250,
  "note": "按信号建仓"
}
```

**响应 201**：返回完整交易记录对象（含 id、amount、created_at）。

---

### `DELETE /api/transactions/<user_id>/<tx_id>` 🔒

删除交易记录（仅删记录，**不回滚**持仓和现金）。成功返回 `204`，找不到返回 `404`。

---

## 六、买入信号

### `GET /api/signals` 🔒

获取当日买入信号（含当前用户持仓个性化建议）。

**响应 200**
```json
{
  "trade_date": "2026-06-30",
  "generated_at": "2026-06-30 15:35:12",
  "signals": [
    {
      "code": "515050",
      "name": "5G ETF",
      "prob_up": 0.7234,
      "close": 1.456,
      "pct_chg": 1.23,
      "action": "OPEN",
      "action_label": "建仓",
      "note": ""
    }
  ],
  "count": 3
}
```

`action` 枚举值：`OPEN`（建仓）/ `ADD`（加仓）/ `HOLD`（观望）/ `REDUCE`（减仓）/ `SKIP`（跳过）

---

### `POST /api/run-signals` 🔒🛡️

管理员手动触发买入信号生成（异步，后台线程执行）。

**响应 200**
```json
{ "ok": true }
```

若已有任务在运行，返回 `409`。

---

### `GET /api/run-signals/status` 🔒

查询信号生成任务状态（用于前端轮询进度）。

**响应 200**
```json
{
  "status": "done",
  "started_at": "2026-06-30 15:35:00",
  "finished_at": "2026-06-30 15:35:12",
  "signal_count": 3,
  "log": ["[完成] 信号生成成功"],
  "error": null
}
```

`status` 枚举：`idle` / `running` / `done` / `error`

---

## 七、卖出信号

### `GET /api/sell-signals` 🔒

获取当前用户的卖出信号。触发类型有三种：

| type | 含义 |
|---|---|
| `STOP_LOSS` | 止损（浮亏超阈值） |
| `TAKE_PROFIT` | 止盈（浮盈超阈值） |
| `MODEL_SELL` | 模型看空（prob_down 超阈值） |

**响应 200**
```json
{
  "trade_date": "2026-06-30",
  "generated_at": "2026-06-30 15:36:00",
  "signals": [
    {
      "code": "515220",
      "name": "煤炭ETF",
      "type": "TAKE_PROFIT",
      "type_label": "止盈",
      "cost_price": 1.200,
      "current_price": 1.310,
      "profit_pct": 9.17,
      "prob_down": 0.42
    }
  ],
  "count": 1
}
```

---

### `POST /api/sell-signals/run` 🔒🛡️

管理员手动触发卖出信号生成（异步）。响应 `{ "ok": true }`。

---

## 八、盘中价格告警

### `GET /api/alerts` 🔒

获取当前用户未读告警（按时间倒序，管理员可见全部）。

**响应 200**
```json
{
  "alerts": [
    {
      "id": "alert_20260630_093012_abc",
      "user_id": "suiy",
      "code": "512100",
      "name": "中证1000ETF",
      "type": "STOP_LOSS",
      "type_label": "触及止损",
      "price": 3.41,
      "threshold": 3.45,
      "timestamp": "2026-06-30 09:30:12",
      "dismissed": false
    }
  ],
  "count": 1
}
```

---

### `POST /api/alerts/<alert_id>/dismiss` 🔒

标记单条告警为已读。

**响应 200**：`{ "ok": true }`  
**响应 404**：`{ "error": "告警不存在" }`

---

### `POST /api/alerts/dismiss-all` 🔒

标记当前用户全部告警为已读（管理员标记所有人）。

---

### `POST /api/alerts/run` 🔒🛡️

管理员手动触发盘中价格监控（异步）。

---

## 九、历史信号

### `GET /api/signal-history` 🔒

获取有历史记录的日期列表（最近 90 天，倒序）。

**响应 200**
```json
["2026-06-30", "2026-06-27", "2026-06-26"]
```

---

### `GET /api/signal-history/<date>` 🔒

获取指定日期的历史信号（格式同 `GET /api/signals`）。

日期格式必须为 `YYYY-MM-DD`，无数据返回 `404`。

---

### `GET /api/signal-history/etf/<code>` 🔒

获取某只 ETF 的历史出现记录（所有曾入选日期）。

**响应 200**
```json
[
  { "date": "2026-06-27", "prob_up": 0.6832, "close": 1.412 },
  { "date": "2026-06-20", "prob_up": 0.7104, "close": 1.385 }
]
```

---

## 十、模拟盘胜率

### `GET /api/paper-trades` 🔒

获取模拟盘胜率统计（T+1 开盘价入场、T+N+1 开盘价出场）。

**响应 200**
```json
{
  "summary": {
    "total": 45,
    "win": 28,
    "win_rate": 0.622,
    "avg_return": 0.0312,
    "avg_hold_days": 4.8
  },
  "trades": [...]
}
```

---

### `POST /api/paper-trades/refresh` 🔒🛡️

管理员手动重新计算模拟盘结果。

**请求体（可选）**
```json
{ "days": 30 }
```

不传或为 0 时评估全部历史记录。成功返回最新模拟盘数据。

---

## 十一、行情数据

### `GET /api/realtime-price/<code>` 🔒

获取单只 ETF 实时价格（新浪财经）。无实时数据时回退到本地最新收盘价。

**响应 200**
```json
{
  "code": "515220",
  "name": "煤炭ETF",
  "price": 1.312,
  "open": 1.300,
  "prev_close": 1.298,
  "pct_chg": 1.08,
  "trade_time": "14:50:03",
  "source": "realtime"
}
```

`source` 枚举：`realtime`（新浪实时）/ `local_close`（本地收盘价回退）

---

### `GET /api/realtime-snapshot/<code>` 🔒

获取单只 ETF 盘中实时快照（akshare，含 IOPV 等专有字段）。

后端对全市场 ETF 快照缓存 60 秒（首次调用约需 15 秒）。

**响应 200**
```json
{
  "code": "512100",
  "name": "中证1000ETF",
  "price": 3.577,
  "iopv": 3.564,
  "premium_rt": -0.35,
  "pct_chg": 2.94,
  "vol_ratio": 1.05,
  "wei_bi": 28.93,
  "main_net_inflow": 71830000,
  "main_net_pct": 2.74,
  "outer": 12345678,
  "inner": 14356789,
  "outer_inner": 0.86,
  "turnover": 24.48,
  "amount": 260000000,
  "update_time": "15:00:00",
  "cache_age_s": 12
}
```

**字段说明**

| 字段 | 说明 |
|---|---|
| `iopv` | 基金参考净值（每 15 秒更新） |
| `premium_rt` | 折溢价率（%）。**负值 = 溢价**（市价 > IOPV），**正值 = 折价**（市价 < IOPV，相对低估） |
| `vol_ratio` | 量比：当日每分钟均量 / 过去 5 日每分钟均量，> 1 说明今日成交相对活跃 |
| `wei_bi` | 委比（%）= (买单量 − 卖单量) / (买单量 + 卖单量) × 100，正值买盘占优 |
| `main_net_inflow` | 主力净流入额（元），大单买入 − 大单卖出（单笔 > 20 万） |
| `main_net_pct` | 主力净流入占总成交额的比例（%） |
| `outer` | 外盘成交量（主动买入，攻击性买单成交） |
| `inner` | 内盘成交量（主动卖出，攻击性卖单成交） |
| `outer_inner` | 外 / 内盘比，> 1 买方主动，< 1 卖方主动 |
| `turnover` | 换手率（%） |
| `cache_age_s` | 当前数据距上次拉取的秒数（0~60） |

**失败响应**

- `503`：akshare 拉取失败
- `404`：该代码未在实时数据中找到（停牌或代码错误）

---

### `GET /api/etf-list` 🔒

获取全量 ETF 列表（代码 ↔ 名称映射 + 分类）。

**响应 200**
```json
{
  "names": {
    "512100": "中证1000ETF",
    "510300": "沪深300ETF"
  },
  "categories": {
    "宽基": ["510050", "510300", "512100"],
    "科技": ["159995", "512480", "515070"]
  }
}
```

---

### `GET /api/etf-history/<code>` 🔒

获取 ETF 近 365 天历史 K 线（本地 parquet 文件）。

**响应 200**
```json
[
  { "date": "2026-06-27", "close": 3.512, "open": 3.480, "high": 3.540, "low": 3.470, "volume": 12345678 }
]
```

---

## 十二、模型配置（管理员）

### `GET /api/model-config` 🔒🛡️

获取当前模型配置及各 ETF 校准后阈值。

**响应 200**
```json
{
  "config": {
    "prob_threshold": 0.5,
    "blacklist": [],
    "threshold_overrides": {},
    "stop_loss": 0.05,
    "take_profit": 0.08,
    "sell_prob_threshold": 0.55,
    "trend_filter_strong_prob": 0.65,
    "active_models": { "5": "lgbm_forward5_20260626.pkl" }
  },
  "calibrated": {
    "512100": 0.512,
    "510300": 0.488
  }
}
```

---

### `PUT /api/model-config` 🔒🛡️

更新模型配置。传哪个字段改哪个，有范围校验。

**请求体（所有字段均可选）**
```json
{
  "prob_threshold": 0.52,
  "stop_loss": 0.05,
  "take_profit": 0.10,
  "sell_prob_threshold": 0.55,
  "trend_filter_strong_prob": 0.65,
  "blacklist": ["159915"],
  "threshold_overrides": { "512100": 0.48 }
}
```

| 字段 | 有效范围 |
|---|---|
| `prob_threshold` | 0.30 ~ 0.95 |
| `stop_loss` | 0.01 ~ 0.50 |
| `take_profit` | 0.01 ~ 1.00 |
| `sell_prob_threshold` | 0.40 ~ 0.95 |
| `trend_filter_strong_prob` | 0.50 ~ 0.90 |

---

### `POST /api/model-config/recalibrate` 🔒🛡️

基于历史信号重新校准各 ETF 的概率阈值。

**请求体（可选）**
```json
{ "lookback": 20 }
```

`lookback` 为回溯天数（5~120，默认 20）。

---

### `GET /api/model-versions` 🔒🛡️

列出 `quant/models/saved/` 下所有模型版本文件，标记当前激活版本。

**响应 200**
```json
{
  "versions": [
    { "filename": "lgbm_forward5_20260626.pkl", "size_kb": 234.5, "saved_at": "2026-06-26 18:30", "is_active": true },
    { "filename": "lgbm_forward5_20260624.pkl", "size_kb": 231.2, "saved_at": "2026-06-24 20:15", "is_active": false }
  ],
  "active": "lgbm_forward5_20260626.pkl",
  "forward": 5
}
```

---

### `POST /api/model-versions/activate` 🔒🛡️

将指定模型文件设为激活版本（即时生效，下次信号生成使用新版本）。

**请求体**
```json
{ "filename": "lgbm_forward5_20260624.pkl" }
```

会校验文件存在且结构合法，防路径穿越攻击。

---

## 十三、管理员工具

### `GET /api/backtest` 🔒🛡️

获取回测结果（读取 `quant/backtest/results/*.json`）。

---

### `GET /api/signal-backtest` 🔒🛡️

对真实推送过的历史信号做事后回测（T+N 实际收益）。

**查询参数**：`min_samples=20`（分组统计的最小样本量，默认 20）

**响应 200**
```json
{
  "overall": { "total": 120, "win_rate": 0.618, "avg_return": 0.0285 },
  "by_category": { "科技": { "win_rate": 0.67, "avg_return": 0.032 } },
  "by_prob_bucket": { "0.5-0.6": { "win_rate": 0.55 }, "0.6-0.7": { "win_rate": 0.64 } }
}
```

---

### `GET /api/email-log` 🔒🛡️

获取最近 100 条邮件推送记录（倒序）。

**响应 200**（数组）
```json
[
  { "timestamp": "2026-06-30 15:40:00", "to": "xxx@gmail.com", "subject": "【ETF信号】...", "status": "sent" }
]
```

---

### `GET /api/system-status` 🔒🛡️

获取系统关键文件的存在状态和最后修改时间。

**响应 200**
```json
{
  "signals":    { "exists": true,  "last_modified": "2026-06-30 15:35:12" },
  "thresholds": { "exists": true,  "last_modified": "2026-06-30 15:35:05" },
  "users":      { "exists": true,  "last_modified": "2026-06-28 10:12:00" },
  "email_log":  { "exists": true,  "last_modified": "2026-06-30 15:40:03" },
  "models":     { "exists": true,  "last_modified": "2026-06-26 18:30:00" }
}
```

---

## 附录：错误码约定

| HTTP 状态码 | 含义 |
|---|---|
| `200` | 成功 |
| `201` | 创建成功 |
| `204` | 删除成功（无响应体） |
| `400` | 请求参数错误（响应体含 `error` 字段） |
| `401` | 未登录 |
| `403` | 无权限 |
| `404` | 资源不存在 |
| `409` | 冲突（如任务已在运行） |
| `500` | 服务端处理出错 |
| `503` | 外部服务（akshare/tushare）拉取失败 |

---

## 附录：图标说明

- 🔒 `@require_auth`：需要登录
- 🛡️ `@require_admin`：需要管理员权限（同时也需要登录）
