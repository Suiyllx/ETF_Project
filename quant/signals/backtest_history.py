"""
backtest_history.py
─────────────────────
对 quant/signals/history/*.json 里已生成的历史买入信号做事后回测：
用本地行情数据算出每条信号在 forward 个交易日后的真实涨跌，统计整体胜率/平均收益，
并支持按指标（ma_dev_20 / mom_20 / rsi_14 等）分组对比，用于验证趋势过滤等候选规则是否有效。

用法：
    python -m quant.signals.backtest_history                       # 整体统计
    python -m quant.signals.backtest_history --group-by ma_dev_20  # 按指标正负分组对比
    python -m quant.signals.backtest_history --min-samples 30      # 样本不足时给出提示而非强行下结论
"""

import argparse
import json
from pathlib import Path

import pandas as pd

from quant.data.fetch_historical import SAVE_DIR

HISTORY_DIR = Path(__file__).parent / "history"


def load_signal_history() -> pd.DataFrame:
    """读取所有历史信号 JSON，展开成一行一信号的 DataFrame。"""
    rows = []
    for f in sorted(HISTORY_DIR.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        trade_date = data["trade_date"]
        for s in data["signals"]:
            row = {
                "trade_date": trade_date,
                "code": s["code"],
                "name": s["name"],
                "prob_up": s["prob_up"],
                "forward": s.get("forward", 5),
            }
            row.update(s.get("indicators", {}))
            rows.append(row)
    return pd.DataFrame(rows)


_price_cache: dict[str, pd.DataFrame | None] = {}


def _load_price(code: str) -> pd.DataFrame | None:
    if code not in _price_cache:
        path = SAVE_DIR / f"{code}.parquet"
        if not path.exists():
            _price_cache[code] = None
        else:
            p = pd.read_parquet(path).sort_values("date").reset_index(drop=True)
            p["date"] = p["date"].astype(str)
            _price_cache[code] = p
    return _price_cache[code]


def forward_return(code: str, trade_date: str, n: int) -> float | None:
    """trade_date 收盘价 → n 个交易日后收盘价的真实涨跌幅，数据不足返回 None。"""
    p = _load_price(code)
    if p is None:
        return None
    idx = p.index[p["date"] == trade_date]
    if len(idx) == 0:
        return None
    i = idx[0]
    if i + n >= len(p):
        return None
    c0, c1 = p.loc[i, "close"], p.loc[i + n, "close"]
    return c1 / c0 - 1


GROUP_BY_METRICS = ["ma_dev_20", "mom_20", "mom_5", "rsi_14", "macd_hist"]


def compute_summary(min_samples: int = 20) -> dict:
    """计算整体统计 + 常用指标分组对比，返回可直接 JSON 序列化的 dict（供 Web API 和 CLI 共用）。"""
    sig_df = load_signal_history()
    sig_df["fwd_ret"] = sig_df.apply(
        lambda r: forward_return(r["code"], r["trade_date"], int(r["forward"])), axis=1
    )
    valid = sig_df.dropna(subset=["fwd_ret"]).copy()

    result = {
        "total_signals": int(len(sig_df)),
        "valid_signals": int(len(valid)),
        "min_samples": min_samples,
        "reliable": len(valid) >= min_samples,
        "overall": None,
        "groups": {},
    }
    if len(valid) == 0:
        return result

    result["overall"] = {
        "hit_rate": float((valid["fwd_ret"] > 0).mean()),
        "mean_ret": float(valid["fwd_ret"].mean()),
    }

    for metric in GROUP_BY_METRICS:
        if metric not in valid.columns:
            continue
        valid["_group"] = valid[metric] >= 0
        g = valid.groupby("_group")["fwd_ret"].agg(
            count="count", mean_ret="mean", hit_rate=lambda x: (x > 0).mean()
        )
        result["groups"][metric] = {
            "positive": _group_row(g, True),
            "negative": _group_row(g, False),
        }
    return result


def _group_row(g: pd.DataFrame, key: bool) -> dict | None:
    if key not in g.index:
        return None
    row = g.loc[key]
    return {"count": int(row["count"]), "mean_ret": float(row["mean_ret"]), "hit_rate": float(row["hit_rate"])}


def run_backtest(group_by: str | None = None, min_samples: int = 20) -> None:
    summary = compute_summary(min_samples=min_samples)
    print(f"历史信号总数：{summary['total_signals']}")
    print(f"已有完整 forward 期真实结果的信号数：{summary['valid_signals']}\n")

    if summary["overall"] is None:
        print("暂无可回测的信号（forward 期还未走完），请等待更多交易日后再跑。")
        return

    print(f"整体胜率（fwd_ret>0）：{summary['overall']['hit_rate']:.1%}　平均收益：{summary['overall']['mean_ret']:.2%}")

    if not summary["reliable"]:
        print(
            f"\n[警告] 样本数 {summary['valid_signals']} 低于 --min-samples {min_samples}，"
            "以下分组统计仅供参考，不建议据此调整过滤规则。"
        )

    if group_by:
        g = summary["groups"].get(group_by)
        if g is None:
            print(f"\n指标 {group_by} 不在信号数据里，可选：{GROUP_BY_METRICS}")
            return
        print(f"\n按 {group_by} 正负分组：")
        for label, key in ((f"{group_by} >= 0", "positive"), (f"{group_by} < 0", "negative")):
            row = g[key]
            if row:
                print(f"  {label}: count={row['count']} mean_ret={row['mean_ret']:.4f} hit_rate={row['hit_rate']:.1%}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--group-by", type=str, default=None, help="按某个指标正负分组对比，如 ma_dev_20 / mom_20")
    parser.add_argument("--min-samples", type=int, default=20, help="样本数低于此值时提示结论不可靠")
    args = parser.parse_args()
    run_backtest(group_by=args.group_by, min_samples=args.min_samples)
