# BO3 PS4 offsets

Build-specific reverse-engineering evidence for Call of Duty: Black Ops III on PS4. This repository accompanies the native [GSCIL compiler and injector](https://github.com/GSCIL/gscil).

The initial profile is **CUSA02624 v1.33**, identified by the SHA256 of the locally analysed ELF: `280c465354eab22136653083e2b533a1bdcf1988e2d407527ec9d2ef4537b616`.

Addresses are **RVAs**, not session pointers. Add the game's module base when interpreting an RVA in a running process. Every entry states its evidence and confidence. `decompiled` means static binary analysis; it does not mean the handler was called successfully on a console. A matching build hash and an address alone do not establish a complete callable ABI.

## Contents

- `data/CUSA02624/1.33/`: one JSON-compatible YAML file per independently evidenced symbol.
- `profiles.json`: build identity and executable RVA ranges.
- `docs/offsets.json`: generated, validated index.
- `tools/`: dependency-free validation and index generation.

No game binaries, IDA databases, dumps, runtime allocations or connection information are distributed. Initial entries document three VM call handlers, not a complete builtin catalog.

## Validate and regenerate

Requires Python 3.10 or later; no third-party packages.

```sh
python -m unittest discover -s tests -v
python -m tools.validate
python -m tools.build
python -m tools.build --check
```

Keep one file per symbol/build. Required metadata includes `id`, title/version/module, kind, RVA, confidence, evidence, description and provenance. Optional AOB signatures are byte patterns, not a promise of compatibility with another update. Confidence levels: `verified-live`, `decompiled`, `inferred`, `guess`. Live confidence requires an actual recorded console observation.
