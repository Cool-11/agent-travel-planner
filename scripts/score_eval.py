#!/usr/bin/env python3
"""
agent-travel-planner 评测打分脚本

指标：
- 成功率：HTTP 200 且 body.ok=True 的样本比例
- 完成率：成功样本中含所有必需字段（景点 / 天气 / 酒店 / 行程）的比例
- 幻觉率：must_include 关键词缺失比例
- 平均时延：所有成功样本的平均响应时间

用法：
  python -m scripts.score_eval --baseline results_baseline.json --current results_current.json
  python -m scripts.score_eval --single results_baseline.json
"""
import argparse
import json
from pathlib import Path

REQUIRED_FIELDS = ["attractions", "weather", "hotel", "itinerary"]


def is_complete(body):
    if not isinstance(body, dict):
        return False
    return all(body.get(field) for field in REQUIRED_FIELDS)


def score_one(run):
    results = run["results"]
    total = len(results)
    success = [r for r in results if r["ok"]]
    n_success = len(success)
    completed = [r for r in success if is_complete(r["body"])]
    n_completed = len(completed)

    from tests.eval_cases import EVAL_CASES
    case_map = {c["name"]: c for c in EVAL_CASES}

    total_must = 0
    missing = 0
    spurious = 0
    for r in success:
        body = r["body"]
        if not isinstance(body, dict):
            continue
        plan_text = json.dumps(body, ensure_ascii=False)
        case = case_map.get(r["case_name"])
        if not case:
            continue
        for kw in case["must_include"]:
            total_must += 1
            if kw not in plan_text:
                missing += 1
        for kw in case["must_not_include"]:
            if kw and kw in plan_text:
                spurious += 1

    avg_latency = round(sum(r["latency"] for r in success) / n_success, 2) if n_success else 0

    return {
        "label": run.get("label", "unknown"),
        "timestamp": run.get("timestamp"),
        "api": run.get("api"),
        "total": total,
        "raw_success": n_success,
        "raw_completed": n_completed,
        "success_rate": round(n_success / total, 4) if total else 0,
        "completion_rate": round(n_completed / n_success, 4) if n_success else 0,
        "hallucination_rate": round(missing / total_must, 4) if total_must else 0,
        "hallucination_detail": {
            "total_must_include_keywords": total_must,
            "missing_keywords": missing,
            "spurious_keywords": spurious,
            "note": "spurious 需要人工标注 must_not_include 后才有意义",
        },
        "avg_latency_sec": avg_latency,
    }


def print_compare(baseline, current):
    print("")
    print("=" * 78)
    b_label = baseline["label"]
    c_label = current["label"]
    print("  对比: " + b_label + "  ->  " + c_label)
    print("=" * 78)
    print("  " + "指标".ljust(22) + b_label.ljust(14) + c_label.ljust(14) + "变化")
    print("-" * 78)

    def fmt_rate(x):
        return str(round(x * 100, 1)) + "%"

    rows = [
        ("样本数", str(baseline["total"]), str(current["total"]), "-"),
        ("成功率", fmt_rate(baseline["success_rate"]), fmt_rate(current["success_rate"]),
         str(round((current["success_rate"] - baseline["success_rate"]) * 100, 1)) + "pp"),
        ("完成率", fmt_rate(baseline["completion_rate"]), fmt_rate(current["completion_rate"]),
         str(round((current["completion_rate"] - baseline["completion_rate"]) * 100, 1)) + "pp"),
        ("幻觉率", fmt_rate(baseline["hallucination_rate"]), fmt_rate(current["hallucination_rate"]),
         str(round((current["hallucination_rate"] - baseline["hallucination_rate"]) * 100, 1)) + "pp"),
        ("平均时延", str(baseline["avg_latency_sec"]) + "s", str(current["avg_latency_sec"]) + "s",
         str(round(current["avg_latency_sec"] - baseline["avg_latency_sec"], 2)) + "s"),
    ]
    for label, b, c, delta in rows:
        print("  " + label.ljust(22) + b.ljust(14) + c.ljust(14) + delta)
    print("-" * 78)
    print("  注: pp = 百分点。负向改善幻觉率/时延，正向改善成功率/完成率。")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline")
    parser.add_argument("--current")
    parser.add_argument("--single")
    parser.add_argument("--results-dir", default=".")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)

    if args.single:
        run = json.loads((results_dir / args.single).read_text(encoding="utf-8"))
        score = score_one(run)
        print(json.dumps(score, ensure_ascii=False, indent=2))
        return

    if not args.baseline or not args.current:
        parser.error("需要同时指定 --baseline 和 --current，或用 --single")

    baseline = json.loads((results_dir / args.baseline).read_text(encoding="utf-8"))
    current = json.loads((results_dir / args.current).read_text(encoding="utf-8"))
    b_score = score_one(baseline)
    c_score = score_one(current)
    print(json.dumps({"baseline": b_score, "current": c_score}, ensure_ascii=False, indent=2))
    print_compare(b_score, c_score)

    b_ts = baseline.get("timestamp", "-")
    c_ts = current.get("timestamp", "-")
    report_path = results_dir / "EVAL_REPORT.md"
    report_lines = []
    report_lines.append("# 评测对比报告")
    report_lines.append("")
    report_lines.append("## Baseline（" + b_ts + "）")
    report_lines.append("")
    report_lines.append("```")
    report_lines.append(json.dumps(b_score, ensure_ascii=False, indent=2))
    report_lines.append("```")
    report_lines.append("")
    report_lines.append("## Current（" + c_ts + "）")
    report_lines.append("")
    report_lines.append("```")
    report_lines.append(json.dumps(c_score, ensure_ascii=False, indent=2))
    report_lines.append("```")
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print("[score_eval] report saved to " + str(report_path))


if __name__ == "__main__":
    main()
