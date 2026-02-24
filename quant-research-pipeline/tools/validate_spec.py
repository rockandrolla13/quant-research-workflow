#!/usr/bin/env python3
"""Deterministic spec.yaml schema validation. Exit 0=pass, 1=fail."""

import sys
from pathlib import Path
import yaml


def _chk(errs: list, cond: bool, msg: str) -> None:
    if not cond:
        errs.append(msg)


def validate(spec_path: Path) -> list[str]:
    errs: list[str] = []
    try:
        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"YAML parse error: {e}"]
    if not isinstance(spec, dict):
        return ["Root must be a mapping"]

    # Top-level
    for k in ["strategy_id", "version", "status", "hypotheses", "signal",
              "data_schema", "module_apis", "test_plan", "success_criteria"]:
        _chk(errs, k in spec and spec[k] is not None, f"Missing: {k}")
    if errs:
        return errs

    _chk(errs, spec.get("status") in ("draft", "review", "locked"),
         f"status must be draft|review|locked")

    # Hypotheses
    hyp = spec.get("hypotheses") or {}
    for k in ["h0", "h1", "test", "alpha", "effect_size"]:
        _chk(errs, k in hyp and hyp[k] is not None, f"Missing: hypotheses.{k}")
    alpha = hyp.get("alpha")
    if isinstance(alpha, (int, float)):
        _chk(errs, 0 < alpha < 1, f"alpha must be 0<α<1, got {alpha}")

    # Signal
    sig = spec.get("signal") or {}
    _chk(errs, sig.get("name"), "Missing: signal.name")
    _chk(errs, sig.get("formula_latex"), "Missing: signal.formula_latex")
    inputs = sig.get("inputs") or []
    _chk(errs, isinstance(inputs, list) and inputs, "signal.inputs must be non-empty list")
    for i, inp in enumerate(inputs):
        _chk(errs, isinstance(inp, dict) and inp.get("name"), f"signal.inputs[{i}]: missing name")
        _chk(errs, isinstance(inp, dict) and inp.get("dtype"), f"signal.inputs[{i}]: missing dtype")

    # Data schema
    data = spec.get("data_schema") or {}
    _chk(errs, data.get("universe"), "Missing: data_schema.universe")
    _chk(errs, isinstance(data.get("columns"), list) and data.get("columns"),
         "data_schema.columns must be non-empty list")
    splits = data.get("splits") or {}
    for s in ["train", "validate", "holdout"]:
        sp = splits.get(s) or {}
        _chk(errs, sp.get("start") is not None, f"Missing: splits.{s}.start")
        _chk(errs, sp.get("end") is not None, f"Missing: splits.{s}.end")

    # Module APIs
    mods = spec.get("module_apis") or []
    _chk(errs, isinstance(mods, list) and mods, "module_apis must be non-empty list")
    for i, mod in enumerate(mods):
        _chk(errs, isinstance(mod, dict) and mod.get("module"), f"module_apis[{i}]: missing module")
        funcs = mod.get("functions") if isinstance(mod, dict) else []
        _chk(errs, isinstance(funcs, list) and funcs, f"module_apis[{i}]: functions must be non-empty")
        for j, fn in enumerate(funcs or []):
            _chk(errs, isinstance(fn, dict) and fn.get("name"), f"module_apis[{i}].functions[{j}]: missing name")
            _chk(errs, isinstance(fn, dict) and fn.get("returns") is not None, f"module_apis[{i}].functions[{j}]: missing returns")
            _chk(errs, isinstance(fn, dict) and fn.get("description"), f"module_apis[{i}].functions[{j}]: missing description")

    # Test plan
    tests = spec.get("test_plan") or {}
    unit = tests.get("unit_tests") or []
    _chk(errs, isinstance(unit, list) and unit, "test_plan.unit_tests must be non-empty list")
    for i, ut in enumerate(unit):
        _chk(errs, isinstance(ut, dict) and ut.get("function"), f"unit_tests[{i}]: missing function")
        _chk(errs, isinstance(ut, dict) and isinstance(ut.get("cases"), list), f"unit_tests[{i}]: cases must be list")
    for i, pt in enumerate(tests.get("property_tests") or []):
        _chk(errs, isinstance(pt, dict) and pt.get("invariant"), f"property_tests[{i}]: missing invariant")

    # Success criteria
    sc = spec.get("success_criteria") or {}
    metrics = sc.get("metrics") or []
    _chk(errs, isinstance(metrics, list) and metrics, "success_criteria.metrics must be non-empty list")
    for i, m in enumerate(metrics):
        _chk(errs, isinstance(m, dict) and m.get("name"), f"metrics[{i}]: missing name")
        _chk(errs, isinstance(m, dict) and m.get("threshold") is not None, f"metrics[{i}]: missing threshold")
        _chk(errs, isinstance(m, dict) and m.get("direction") in (">", "<"), f"metrics[{i}]: direction must be >|<")

    return errs


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <spec.yaml>", file=sys.stderr)
        sys.exit(1)
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"❌ Not found: {path}", file=sys.stderr)
        sys.exit(1)
    errs = validate(path)
    if errs:
        print(f"❌ FAILED ({len(errs)} errors):")
        for i, e in enumerate(errs, 1):
            print(f"  {i}. {e}")
        sys.exit(1)
    print("✅ PASSED")


if __name__ == "__main__":
    main()
