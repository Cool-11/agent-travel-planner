#!/usr/bin/env python3
"""
agent-travel-planner 评测脚本

用法：
  python -m scripts.run_eval --baseline   # 跑原始版本（无 ToolDispatcher 等改进）
  python -m scripts.run_eval              # 跑当前代码
  python -m scripts.run_eval --output results.json
  python -m scripts.run_eval --api http://localhost:8000

输出：results.json 含每条 case 的耗时、HTTP 状态、返回字段。
"""
import argparse
import json
import time
import urllib.request
import urllib.error
import sys
from pathlib import Path

# 让脚本能 import 项目根目录的 tests.eval_cases
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tests.eval_cases import EVAL_CASES


def call_agent(payload: dict, api_base: str, timeout: int = 180) -> dict:
    """调用 agent-travel-planner 后端 /api/trip/plan，返回标准化 dict"""
    url = f"{api_base.rstrip(chr(47))}/api/trip/plan"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return {
                "ok": True,
                "status": resp.status,
                "latency": round(time.time() - t0, 2),
                "body": body,
                "error": None,
            }
    except urllib.error.HTTPError as e:
        return {
            "ok": e.code < 500,
            "status": e.code,
            "latency": round(time.time() - t0, 2),
            "body": None,
            "error": f"HTTP {e.code}: {e.reason}",
        }
    except urllib.error.URLError as e:
        return {
            "ok": False,
            "status": None,
            "latency": round(time.time() - t0, 2),
            "body": None,
            "error": f"URLError: {e.reason}",
        }
    except Exception as e:
        return {
            "ok": False,
            "status": None,
            "latency": round(time.time() - t0, 2),
            "body": None,
            "error": f"{type(e).__name__}: {e}",
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://localhost:8000", help="后端地址")
    parser.add_argument("--output", default="results.json", help="输出文件")
    parser.add_argument("--baseline", action="store_true", help="标记为 baseline 运行")
    parser.add_argument("--label", default=None, help="运行标签（默认根据 --baseline 自动）")
    parser.add_argument("--limit", type=int, default=None, help="只跑前 N 条")
    args = parser.parse_args()

    label = args.label or ("baseline" if args.baseline else "current")
    cases = EVAL_CASES[:args.limit] if args.limit else EVAL_CASES

    print(f"[run_eval] label={label} api={args.api} cases={len(cases)}")
    results = []
    for i, case in enumerate(cases, 1):
        payload = {
            "destination": case["input"]["destination"],
            "days": case["input"]["days"],
            "preferences": case["input"]["preferences"],
            "budget": case["input"]["budget"],
        }
        print(f"  [{i:2d}/{len(cases)}] {case['name']} ...", end=" ", flush=True)
        result = call_agent(payload, args.api)
        record = {
            "case_name": case["name"],
            "category": case["category"],
            "label": label,
            "input": case["input"],
            "ok": result["ok"],
            "status": result["status"],
            "latency": result["latency"],
            "error": result["error"],
            "body": result["body"],
        }
        results.append(record)
        ok_mark = "OK" if result["ok"] else "FAIL"
        print(f"{ok_mark} ({result['latency']}s)")

    summary = {
        "label": label,
        "api": args.api,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(results),
        "success": sum(1 for r in results if r["ok"]),
        "results": results,
    }
    out_path = Path(__file__).resolve().parent.parent / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[run_eval] saved {len(results)} records to {out_path}")
    print(f"[run_eval] success: {summary['success']} / {summary['total']}")


if __name__ == "__main__":
    main()
