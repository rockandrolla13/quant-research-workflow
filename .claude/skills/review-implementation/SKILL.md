Review Codex's implementation of strategy $ARGUMENTS against the locked spec.

## Step 1: Load the contract

Read strategies/$ARGUMENTS/spec/spec.yaml — this is the source of truth.

## Step 2: Check function signatures

For each module in spec.yaml modules[]:
- Open strategies/$ARGUMENTS/repo/src/$ARGUMENTS/{module.filename}
- Verify every function signature matches spec.yaml EXACTLY
- Flag any missing functions, wrong argument names, wrong types, wrong defaults

## Step 3: Check test coverage

For each test in spec.yaml tests.unit[]:
- Open strategies/$ARGUMENTS/repo/tests/test_{module}.py
- Verify the test case exists with the correct input/expected values from spec
- Flag any missing tests or modified expected values

## Step 4: Check config externalisation

Open strategies/$ARGUMENTS/repo/config.yaml
- Every parameter from spec.yaml signal.parameters should be here
- Grep src/ for hardcoded numeric values — flag any that should be in config

## Step 5: Check notebook thinness

Open each notebook in strategies/$ARGUMENTS/repo/notebooks/
- Notebooks should ONLY import from src/ and call functions
- Flag any function definitions or computation logic in notebook cells

## Step 6: Check holdout safety

- Grep for holdout date strings in src/ and notebooks/
- data.splits.holdout.touched must still be false in spec.yaml
- Flag any code that loads data from the holdout period

## Step 7: Report

Present findings as:
- ✅ Compliant items
- ⚠️ Minor deviations (suggest fixes)
- ❌ Spec violations (must fix before proceeding)
