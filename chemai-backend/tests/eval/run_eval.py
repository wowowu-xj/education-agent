# -*- coding: utf-8 -*-
"""障碍诊断评估层：用真实 LLM 跑标注错题集，输出每维度精确率/召回率。

对应 tasks §9.3。加载 ``labeled_dataset.json``，用 ``DashScopeDiagnosisClient``
（真实 DashScope API）逐条跑三引擎诊断，把预测的 barrier_type /
misconception_category 与标注比对，计算每维度（宏观平均 + 各类别）的
精确率 / 召回率，回填 design D9 的 ~90% / ~85% 估算值。

用法（需在 .env 配置 DASHSCOPE_API_KEY）::

    cd chemai-backend
    source venv/bin/activate
    python -m tests.eval.run_eval

结果打印到 stdout，并写入 ``tests/eval/results.json``。
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from chem_skills.chemistry_diagnosis.engine.diagnosis import DiagnosisEngine
from chem_skills.chemistry_diagnosis.engine.llm_client import DashScopeDiagnosisClient

_DATASET = Path(__file__).with_name("labeled_dataset.json")
_RESULTS = Path(__file__).with_name("results.json")

_BARRIER_KEYS = ("concept", "reading", "expression")
_MISCONCEPTION_KEYS = (
    "chemical_equilibrium",
    "redox",
    "mole_calculation",
    "organic_chemistry",
    "chemical_notation",
    "structure_properties",
)


@dataclass
class _Metrics:
    """一类别的精确率/召回率累加器。"""

    tp: int = 0
    fp: int = 0
    fn: int = 0

    @property
    def precision(self) -> float:
        denom = self.tp + self.fp
        return round(self.tp / denom, 3) if denom else 0.0

    @property
    def recall(self) -> float:
        denom = self.tp + self.fn
        return round(self.tp / denom, 3) if denom else 0.0


def _macro(metrics: dict[str, _Metrics]) -> dict[str, float]:
    """宏观平均精确率/召回率（各类别简单平均）。"""
    keys = [k for k in metrics if metrics[k].tp + metrics[k].fn > 0]
    if not keys:
        return {"precision": 0.0, "recall": 0.0}
    return {
        "precision": round(sum(metrics[k].precision for k in keys) / len(keys), 3),
        "recall": round(sum(metrics[k].recall for k in keys) / len(keys), 3),
    }


def _render(metrics: dict[str, _Metrics]) -> list[dict]:
    """把指标累加器渲染成按 key 排序的行列表。"""
    return [
        {
            "class": key,
            "precision": metrics[key].precision,
            "recall": metrics[key].recall,
            "tp": metrics[key].tp,
            "fp": metrics[key].fp,
            "fn": metrics[key].fn,
        }
        for key in sorted(metrics)
    ]


def main() -> None:
    """加载数据集 → 逐条诊断 → 计算双维度指标 → 打印并落盘。"""
    dataset = json.loads(_DATASET.read_text(encoding="utf-8"))
    items = dataset["items"]

    engine = DiagnosisEngine(DashScopeDiagnosisClient())

    barrier_metrics: dict[str, _Metrics] = defaultdict(_Metrics)
    misconception_metrics: dict[str, _Metrics] = defaultdict(_Metrics)
    detail: list[dict] = []

    for item in items:
        outcome = engine.diagnose_one(
            student_answer=item["student_answer"],
            question_text=item["question_text"],
        )
        fusion = outcome.fusion
        pred_barrier = fusion.barrier_type.value if fusion.barrier_type else None
        pred_mis = fusion.misconception_category

        true_barrier = item["barrier_type"]
        true_mis = item["misconception_category"]

        if pred_barrier == true_barrier:
            barrier_metrics[true_barrier].tp += 1
        else:
            barrier_metrics[true_barrier].fn += 1
            if pred_barrier is not None:
                barrier_metrics[pred_barrier].fp += 1

        if pred_mis == true_mis:
            misconception_metrics[true_mis].tp += 1
        else:
            misconception_metrics[true_mis].fn += 1
            if pred_mis is not None:
                misconception_metrics[pred_mis].fp += 1

        detail.append(
            {
                "id": item["id"],
                "true_barrier": true_barrier,
                "pred_barrier": pred_barrier,
                "true_misconception": true_mis,
                "pred_misconception": pred_mis,
                "confidence": fusion.confidence,
                "needs_review": fusion.needs_review,
                "fallback_reason": fusion.fallback_reason,
            }
        )

    report = {
        "total": len(items),
        "barrier_type": {
            "macro": _macro(barrier_metrics),
            "per_class": _render(barrier_metrics),
        },
        "misconception_category": {
            "macro": _macro(misconception_metrics),
            "per_class": _render(misconception_metrics),
        },
        "detail": detail,
    }

    _RESULTS.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
