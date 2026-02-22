#!/usr/bin/env python3
"""Deterministic spec.yaml gate. No LLM. Pure schema check.

Exit 0 = pass, exit 1 = fail.
Uses only stdlib + pyyaml. No other deps.
"""

import sys
from pathlib import Path

import yaml


def _check(errors: list[str], condition: bool, msg: str) -> None:
    if not condition:
        errors.append(msg)


def validate(spec_path: Path) -> list[str]:
    """Validate spec.yaml and return list of error strings (empty = pass)."""
    errors: list[str] = []

    # --- Load ---
    try:
        with open(spec_path, "r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)
    except Exception as e:
        return [f"Failed to parse YAML: {e}"]

    if not isinstance(spec, dict):
        return ["spec.yaml root must be a mapping"]

    # --- Top-level required keys ---
    top_required = [
        "strategy_id", "version", "status",
        "hypotheses", "signal", "data_schema",
        "module_apis", "test_plan", "success_criteria",
    ]
    for key in top_required:
        _check(errors, key in spec and spec[key] is not None,
               f"Missing or null top-level field: {key}")

    if errors:
        return errors  # can't continue without structure

    # --- status ---
    _check(errors, spec.get("status") in ("draft", "review", "locked"),
           f"status must be draft|review|locked, got: {spec.get('status')}")

    # --- hypotheses ---
    hyp = spec.get("hypotheses", {}) or {}
    for key in ["h0", "h1", "test", "alpha", "effect_size"]:
        _check(errors, key in hyp and hyp[key] is not None,
               f"Missing or null: hypotheses.{key}")
    alpha = hyp.get("alpha")
    if isinstance(alpha, (int, float)):
        _check(errors, 0 < alpha < 1,
               f"hypotheses.alpha must be 0 < alpha < 1, got: {alpha}")

    # --- signal ---
    sig = spec.get("signal", {}) or {}
    _check(errors, sig.get("name"), "Missing: signal.name")
    _check(errors, sig.get("formula_latex"), "Missing: signal.formula_latex")
    inputs = sig.get("inputs")
    _check(errors, isinstance(inputs, list) and len(inputs) > 0,
           "signal.inputs must be a non-empty list")
    if isinstance(inputs, list):
        for i, inp in enumerate(inputs):
            _check(errors, isinstance(inp, dict) and inp.get("name"),
                   f"signal.inputs[{i}]: missing name")
            _check(errors, isinstance(inp, dict) and inp.get("dtype"),
                   f"signal.inputs[{i}]: missing dtype")

    # --- data_schema ---
    data = spec.get("data_schema", {}) or {}
    _check(errors, data.get("universe"), "Missing: data_schema.universe")
    cols = data.get("columns")
    _check(errors, isinstance(cols, list) and len(cols) > 0,
           "data_schema.columns must be a non-empty list")
    splits = data.get("splits", {}) or {}
    for split_name in ["train", "validate", "holdout"]:
        s = splits.get(split_name, {}) or {}
        _check(errors, s.get("start") is not None,
               f"Missing: data_schema.splits.{split_name}.start")
        _check(errors, s.get("end") is not None,
               f"Missing: data_schema.splits.{split_name}.end")

    # --- module_apis ---
    modules = spec.get("module_apis")
    _check(errors, isinstance(modules, list) and len(modules) > 0,
           "module_apis must be a non-empty list")
    if isinstance(modules, list):
        for i, mod in enumerate(modules):
            _check(errors, isinstance(mod, dict) and mod.get("module"),
                   f"module_apis[{i}]: missing module name")
            funcs = mod.get("functions") if isinstance(mod, dict) else None
            _check(errors, isinstance(funcs, list) and len(funcs) > 0,
                   f"module_apis[{i}]: functions must be a non-empty list")
            if isinstance(funcs, list):
                for j, fn in enumerate(funcs):
                    _check(errors, isinstance(fn, dict) and fn.get("name"),
                           f"module_apis[{i}].functions[{j}]: missing name")
                    _check(errors, isinstance(fn, dict) and fn.get("returns") is not None,
                           f"module_apis[{i}].functions[{j}]: missing returns")
                    _check(errors, isinstance(fn, dict) and fn.get("description"),
                           f"module_apis[{i}].functions[{j}]: missing description")

    # --- test_plan ---
    tests = spec.get("test_plan", {}) or {}
    unit = tests.get("unit_tests")
    _check(errors, isinstance(unit, list) and len(unit) > 0,
           "test_plan.unit_tests must be a non-empty list")
    if isinstance(unit, list):
        for i, ut in enumerate(unit):
            _check(errors, isinstance(ut, dict) and ut.get("function"),
                   f"test_plan.unit_tests[{i}]: missing function")
            _check(errors, isinstance(ut, dict) and isinstance(ut.get("cases"), list),
                   f"test_plan.unit_tests[{i}]: cases must be a list")

    prop = tests.get("property_tests")
    if isinstance(prop, list):
        for i, pt in enumerate(prop):
            _check(errors, isinstance(pt, dict) and pt.get("invariant"),
                   f"test_plan.property_tests[{i}]: missing invariant")

    # --- success_criteria ---
    sc = spec.get("success_criteria", {}) or {}
    metrics = sc.get("metrics")
    _check(errors, isinstance(metrics, list) and len(metrics) > 0,
           "success_criteria.metrics must be a non-empty list")
    if isinstance(metrics, list):
        for i, m in enumerate(metrics):
            _check(errors, isinstance(m, dict) and m.get("name"),
                   f"success_criteria.metrics[{i}]: missing name")
            _check(errors, isinstance(m, dict) and m.get("threshold") is not None,
                   f"success_criteria.metrics[{i}]: missing threshold")
            _check(errors, isinstance(m, dict) and m.get("direction") in (">", "<"),
                   f"success_criteria.metrics[{i}]: direction must be '>' or '<'")

    return errors


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path/to/spec.yaml>", file=sys.stderr)
        sys.exit(1)

    spec_path = Path(sys.argv[1])
    if not spec_path.exists():
        print(f"❌ File not found: {spec_path}", file=sys.stderr)
        sys.exit(1)

    errors = validate(spec_path)

    if errors:
        print(f"❌ spec.yaml validation FAILED ({len(errors)} errors):\n")
        for i, err in enumerate(errors, 1):
            print(f"  {i}. {err}")
        sys.exit(1)
    else:
        print("✅ spec.yaml validation PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
