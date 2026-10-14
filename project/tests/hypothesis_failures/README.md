# Hypothesis failure logs (spec §6.4)

When `test_random_proper_dictionary_agrees_with_oracle` fails, pytest writes
`latest.json` here with:

- `seed`
- `dictionary` (rule index and hex left/right tokens)
- `input` (hex)
- `smallest_known_counterexample` (the same fields after Hypothesis shrinking)

JSON files in this directory are generated artefacts and are gitignored. After a
failure, copy the smallest example into a permanent regression test; do not
delete the log until that is done.
