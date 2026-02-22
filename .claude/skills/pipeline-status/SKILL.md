Show the pipeline status for strategy $ARGUMENTS.

```bash
.venv-extract/bin/python tools/update_state.py strategies/$ARGUMENTS --status
```

If the status script doesn't exist yet, check manually:

1. **extract:** Does strategies/$ARGUMENTS/extract/raw.md exist and have content?
2. **synth:** Do strategies/$ARGUMENTS/synth/strategy.md and formula.md exist?
3. **spec:** Does strategies/$ARGUMENTS/spec/spec.yaml exist? Run validate_spec.py on it.
4. **review:** Does strategies/$ARGUMENTS/spec/review.md exist? What's the verdict?
5. **locked:** Does `git tag -l "spec-$ARGUMENTS-*"` return a tag?
6. **implemented:** Does strategies/$ARGUMENTS/repo/src/ have Python files?
7. **tested:** Does `cd strategies/$ARGUMENTS/repo && .venv-stratpipe/bin/python -m pytest` pass?
8. **tex:** Does strategies/$ARGUMENTS/tex/note.tex exist?

Report the status table and suggest the next action.
