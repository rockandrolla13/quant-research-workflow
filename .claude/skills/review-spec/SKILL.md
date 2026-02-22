Review the spec for strategy $ARGUMENTS by calling Gemini, then fix any issues.

## Step 1: Validate gate first

```bash
.venv-extract/bin/python tools/validate_spec.py strategies/$ARGUMENTS/spec/spec.yaml
```

If this fails, fix spec.yaml until it passes. Do not call Gemini on an invalid spec.

## Step 2: Call Gemini

```bash
.venv-extract/bin/python tools/call_gemini.py --mode review \
  --spec strategies/$ARGUMENTS/spec/spec.yaml \
  --formula strategies/$ARGUMENTS/synth/formula.md \
  --output strategies/$ARGUMENTS/spec/review.md
```

## Step 3: Read review and act

Read strategies/$ARGUMENTS/spec/review.md.

For each item:
- PASS → no action
- WARN → fix if straightforward (missing assumption, minor notation), otherwise note for user
- FAIL → fix spec.yaml, re-run validate_spec.py, re-run this Gemini review

## Step 4: Loop

If you made fixes, re-run Steps 1-3 until review is PASS or PASS WITH WARNINGS only.
Maximum 3 loops. If still FAIL after 3, present the remaining issues to the user.

## Step 5: Report

Tell the user:
- Final review verdict
- What you fixed (if anything)
- Any remaining warnings that need human judgment
