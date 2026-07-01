"""
sync_etf_names.py
一次性维护脚本：把 portfolios/*.json（持仓）和 *_transactions.json（交易记录）里
按 code 存的 ETF 名字，与 quant/utils/etf_list.py 里的最新名称对齐。

背景：持仓/交易记录里的 name 字段是导入/交易时写死的字符串，不会随 etf_list.py
改名（如 C4 的 516780 环保ETF→稀土ETF）自动更新，导致新旧环境显示不一致。

用法：
    python sync_etf_names.py            # 预览将要修改的内容，不写入
    python sync_etf_names.py --apply    # 实际写入修改
"""
import argparse
import json
from pathlib import Path

from quant.utils.etf_list import ETF_LIST

ROOT = Path(__file__).parent
CODE_NAME = {e["code"]: e["name"] for e in ETF_LIST}


def sync_file(path: Path, apply: bool) -> int:
    if not path.exists():
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = 0

    if isinstance(data, dict) and "positions" in data:
        records, name_key = data["positions"], "name"
    elif isinstance(data, list):
        records, name_key = data, "etf_name"
    else:
        return 0

    for r in records:
        code = r.get("code") or r.get("etf_code")
        correct = CODE_NAME.get(code)
        if correct and r.get(name_key) != correct:
            print(f"  [{path.name}] {code}: {r.get(name_key)!r} -> {correct!r}")
            r[name_key] = correct
            changed += 1

    if changed and apply:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return changed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="实际写入，默认只预览")
    args = parser.parse_args()

    total = 0
    for path in sorted((ROOT / "portfolios").glob("*.json")):
        if path.name == "users.json":
            continue
        total += sync_file(path, args.apply)

    if total == 0:
        print("未发现名称不一致，无需修改。")
    elif args.apply:
        print(f"\n已修复 {total} 处名称。")
    else:
        print(f"\n共发现 {total} 处名称不一致（预览模式，未写入）。加 --apply 执行修复。")


if __name__ == "__main__":
    main()
