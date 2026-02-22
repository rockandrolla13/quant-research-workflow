Scaffold a new strategy directory for $ARGUMENTS.

If tools/init_strategy.sh exists:
```bash
bash tools/init_strategy.sh $ARGUMENTS
```

Otherwise, create the structure manually:
```bash
mkdir -p strategies/$ARGUMENTS/{input,extract,synth,spec,repo/src/$ARGUMENTS,repo/tests,repo/notebooks,tex}
touch strategies/$ARGUMENTS/repo/src/$ARGUMENTS/__init__.py
touch strategies/$ARGUMENTS/repo/tests/__init__.py
```

Then create strategies/$ARGUMENTS/input/meta.json:
```json
{
  "strategy_id": "$ARGUMENTS",
  "title": "",
  "authors": [],
  "date": "",
  "source_url": "",
  "notes": ""
}
```

Tell the user: "Strategy $ARGUMENTS scaffolded. Drop the PDF at strategies/$ARGUMENTS/input/source.pdf, then run /process-pdf $ARGUMENTS"
