"""routes/market.py — 行情相关 API（实时价、ETF 列表、历史 K 线）"""

import math
import threading
import time

from flask import Blueprint, jsonify

from routes._shared import require_auth

market_bp = Blueprint("market", __name__)

# ── ETF 实时快照缓存（akshare 全量拉取约 15s，缓 60s 避免频繁等待）──
_snap_cache: dict = {"df": None, "ts": 0.0}
_snap_lock = threading.Lock()
_SNAP_TTL = 60  # seconds


def _fetch_etf_snapshot():
    """返回 akshare fund_etf_spot_em() 结果，60s 内复用缓存。"""
    import akshare as ak
    now = time.time()
    with _snap_lock:
        if _snap_cache["df"] is None or now - _snap_cache["ts"] > _SNAP_TTL:
            _snap_cache["df"] = ak.fund_etf_spot_em()
            _snap_cache["ts"] = time.time()
        return _snap_cache["df"]


def _sf(val, digits=4):
    """Safe float：NaN/Inf 转 None，否则 round。"""
    try:
        v = float(val)
        return None if (math.isnan(v) or math.isinf(v)) else round(v, digits)
    except Exception:
        return None


def _sina_code(code: str) -> str:
    return ("sh" if (code.startswith("5") and not code.startswith("159")) else "sz") + code


@market_bp.get("/api/realtime-price/<code>")
@require_auth
def api_realtime_price(code):
    import urllib.request
    from quant.utils.etf_list import CODE_TO_NAME

    sina_code = _sina_code(code)
    try:
        url = f"https://hq.sinajs.cn/list={sina_code}"
        req = urllib.request.Request(url, headers={
            "Referer":    "https://finance.sina.com.cn",
            "User-Agent": "Mozilla/5.0",
        })
        with urllib.request.urlopen(req, timeout=4) as resp:
            text = resp.read().decode("gbk", errors="replace")

        inner = text.split('"')[1] if '"' in text else ""
        parts = inner.split(",")
        if len(parts) >= 10 and parts[3]:
            current    = float(parts[3])
            open_p     = float(parts[1]) if parts[1] else current
            prev_close = float(parts[2]) if parts[2] else current
            pct_chg    = round((current - prev_close) / prev_close * 100, 2) if prev_close else 0
            trade_time = parts[31] if len(parts) > 31 else ""
            return jsonify({
                "code":       code,
                "name":       CODE_TO_NAME.get(code, code),
                "price":      round(current, 4),
                "open":       round(open_p, 4),
                "prev_close": round(prev_close, 4),
                "pct_chg":    pct_chg,
                "trade_time": trade_time,
                "source":     "realtime",
            })
    except Exception:
        pass

    try:
        from quant.data.fetch_historical import load
        df = load(code)
        if df is not None and not df.empty:
            last = df.iloc[-1]
            return jsonify({
                "code":       code,
                "name":       CODE_TO_NAME.get(code, code),
                "price":      round(float(last["close"]), 4),
                "open":       round(float(last.get("open", last["close"])), 4),
                "prev_close": round(float(last["close"]), 4),
                "pct_chg":    0.0,
                "trade_time": str(last.get("date", ""))[:10],
                "source":     "local_close",
            })
    except Exception:
        pass

    return jsonify({"error": "无法获取行情"}), 404


@market_bp.get("/api/realtime-snapshot/<code>")
@require_auth
def api_realtime_snapshot(code):
    """
    返回单只 ETF 的实时盘口数据（IOPV、委比、主力净流入、外内盘等）。
    数据来源：akshare fund_etf_spot_em()，后端缓存 60s。
    """
    try:
        df = _fetch_etf_snapshot()
    except Exception as e:
        return jsonify({"error": f"行情拉取失败：{e}"}), 503

    row = df[df["代码"] == code]
    if row.empty:
        return jsonify({"error": "未在实时数据中找到该 ETF"}), 404

    r = row.iloc[0]

    outer = _sf(r.get("外盘"))
    inner = _sf(r.get("内盘"))
    outer_inner = round(outer / inner, 2) if (outer and inner and inner != 0) else None

    # 折溢价符号说明：akshare 基金折价率 = (IOPV - 市价) / 市价 × 100
    # 正数 = 折价（市价低于 IOPV）；负数 = 溢价（市价高于 IOPV）
    premium_rt = _sf(r.get("基金折价率"))

    cache_age = round(time.time() - _snap_cache["ts"])

    return jsonify({
        "code":            code,
        "name":            str(r.get("名称", "")),
        "price":           _sf(r.get("最新价")),
        "iopv":            _sf(r.get("IOPV实时估值")),
        "premium_rt":      premium_rt,   # 正=折价/负=溢价
        "pct_chg":         _sf(r.get("涨跌幅")),
        "vol_ratio":       _sf(r.get("量比"), 2),
        "wei_bi":          _sf(r.get("委比"), 2),
        "main_net_inflow": _sf(r.get("主力净流入-净额"), 0),
        "main_net_pct":    _sf(r.get("主力净流入-净占比"), 2),
        "outer":           outer,
        "inner":           inner,
        "outer_inner":     outer_inner,
        "turnover":        _sf(r.get("换手率"), 2),
        "amount":          _sf(r.get("成交额"), 0),
        "update_time":     str(r.get("更新时间", "")),
        "cache_age_s":     cache_age,
    })


@market_bp.get("/api/etf-list")
@require_auth
def api_etf_list():
    from quant.utils.etf_list import CODE_TO_NAME, ETF_CATEGORIES
    return jsonify({"names": CODE_TO_NAME, "categories": ETF_CATEGORIES})


@market_bp.get("/api/etf-history/<code>")
@require_auth
def api_etf_history(code):
    try:
        from quant.data.fetch_historical import load
        df = load(code)
        if df is None or df.empty:
            return jsonify([])
        df      = df.tail(365).reset_index()
        records = []
        for _, row in df.iterrows():
            date_val = row.get("date") or row.get("trade_date") or str(row.name)
            records.append({
                "date":   str(date_val)[:10],
                "close":  round(float(row.get("close",  0)), 4),
                "open":   round(float(row.get("open",   row.get("close", 0))), 4),
                "high":   round(float(row.get("high",   row.get("close", 0))), 4),
                "low":    round(float(row.get("low",    row.get("close", 0))), 4),
                "volume": float(row.get("volume", 0)),
            })
        return jsonify(records)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
