---
name: sepia-opt-burstiness
description: OPTIONAL sepia add-on. Diagnoses and calibrates sentence-length burstiness (variance / alternation pattern) toward the human range. Use only when the user explicitly asks to target GPTZero-style "mixed"/"AI" flags or to vary sentence rhythm. This skill is OPTIONAL — never auto-load; ask the user before applying.
version: 0.1.0
metadata:
  optional: true
  ask-before-load: true
---

> ⚠️ **OPTIONAL SKILL — ASK BEFORE USING.**
> This skill is **not** part of core sepia and is **not** loaded by default.
> Before you apply any of its operations, you **MUST** ask the user:
> *"Enable optional burstiness calibration for this document? It adjusts sentence-length variance toward the human range; it may or may not change detector scores, and sepia core deliberately does not use this axis."*
> Only proceed if the user says yes. If they decline, do nothing.

# sepia-opt-burstiness (optional)

A standalone, opt-in calibration pass. GPTZero and similar detectors lean on
**burstiness** — the variance and alternation pattern of sentence lengths. Human
prose shows more variation; mechanically uniform text reads as machine-written.

Core sepia intentionally excludes mean sentence length / paragraph length as
signals (the underlying research gives contradictory directions). This optional
skill covers that axis **as calibration toward the human distribution**, never as
detector evasion.

## What it does
- **Diagnose** — run `scripts/measure.py` to report sentence count, mean length,
  coefficient of variation (CV), alternation index, and a human-band judgment.
- **Calibrate** — rewrite toward a human burstiness band (CV ≈ 0.45–1.1): merge
  consecutive short sentences, split over-long ones, and deliberately alternate
  short/long rhythm instead of a steady beat.

## How to run the diagnostic
```bash
<PY> skills/sepia-opt-burstiness/scripts/measure.py "<file-or-stdin>.txt"
```
- `<PY>` = a Python 3.10+ interpreter (standard library only; no install needed).
- Reads a file path argument, or falls back to stdin.

## Calibration moves (apply only after the user opts in)
1. **Break monotony** — if CV < 0.45, find runs of similarly sized sentences and
   merge two shorts into one, or split one long into two.
2. **Alternate** — follow a long sentence with a short one; avoid 3+ sentences of
   the same length in a row.
3. **Keep meaning** — calibration must not alter facts, claims, or the user's
   voice beyond rhythm.

## Limitations
- Pure heuristic; the human band is approximate.
- Does **not** guarantee a detector will stop flagging the text.
- Not a substitute for sepia's structural passes; use alongside, not instead of.
