---
name: sepia-opt-perplexity
description: OPTIONAL sepia add-on. Diagnoses and calibrates a perplexity proxy (lexical surprise via TTR, rare-word ratio, self-entropy) toward the human range. Use only when the user explicitly asks to target GPTZero-style "mixed"/"AI" flags. This skill is OPTIONAL — never auto-load; ask the user before applying.
version: 0.1.0
metadata:
  optional: true
  ask-before-load: true
---

> ⚠️ **OPTIONAL SKILL — ASK BEFORE USING.**
> This skill is **not** part of core sepia and is **not** loaded by default.
> Before you apply any of its operations, you **MUST** ask the user:
> *"Enable optional perplexity calibration for this document? It estimates a perplexity proxy and nudges lexical surprise toward the human range; it may or may not change detector scores, and sepia core deliberately does not use this axis."*
> Only proceed if the user says yes. If they decline, do nothing.

# sepia-opt-perplexity (optional)

Detectors such as GPTZero also use **perplexity** (how "surprising" the text is to
a language model). Human writing is more surprising; AI text is over-smooth and
predictable. This optional skill estimates a **perplexity proxy** with no external
model and can calibrate toward a more human lexical profile.

> **Note:** a true perplexity score needs an LLM API. This skill uses lightweight
> stylometric proxies — type-token ratio, rare-word ratio against a common-word
> list, and character-bigram self-entropy. Treat the numbers as *directional*,
> not exact.

## What it does
- **Diagnose** — run `scripts/measure.py` for TTR, rare-word ratio, self-entropy,
  and a human-band judgment.
- **Calibrate** — raise lexical surprise without breaking clarity: replace vague
  common words with precise/concrete ones, vary syntax, add specifics.

## How to run the diagnostic
```bash
<PY> skills/sepia-opt-perplexity/scripts/measure.py "<file-or-stdin>.txt"
```
- `<PY>` = a Python 3.10+ interpreter (standard library only; no install needed).

## Calibration moves (apply only after the user opts in)
1. Swap generic verbs/nouns for specific ones (e.g., "utilize" → "wield",
   "thing" → a named entity).
2. Vary sentence openers and clause order.
3. Add concrete detail where the text is abstract — but never invent facts.

## Limitations
- Proxy only; real perplexity requires an LM.
- More "surprise" is not always better — over-rare words hurt readability.
- Does **not** guarantee a detector will stop flagging the text.
