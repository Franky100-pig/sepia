#!/usr/bin/env python3
"""Burstiness diagnostic for the optional sepia-opt-burstiness skill.

Standard library only. Reports sentence-length statistics that approximate the
"burstiness" axis GPTZero-style detectors use:
  - CV (coefficient of variation) of sentence word-counts
  - an alternation index (mean adjacent length difference / mean)
Human prose typically sits around CV 0.45-1.1; very low CV reads mechanical.
"""
import sys
import re
import json
import statistics


def read_text(path):
    if path:
        with open(path, encoding="utf-8") as f:
            return f.read()
    return sys.stdin.read()


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words_of(s):
    return re.findall(r"[A-Za-z0-9']+", s)


def analyze(text):
    sents = sentences(text)
    lengths = [len(words_of(s)) for s in sents if words_of(s)]
    n = len(lengths)
    if n < 2:
        return {"sentences": n, "error": "need >=2 sentences to measure burstiness"}
    mean = statistics.mean(lengths)
    sd = statistics.pstdev(lengths)
    cv = sd / mean if mean else 0.0
    diffs = [abs(lengths[i] - lengths[i - 1]) for i in range(1, n)]
    alt = statistics.mean(diffs) / mean if mean else 0.0
    if cv < 0.45:
        band = "too uniform (mechanical) — raise variation"
    elif cv > 1.1:
        band = "highly variable — usually fine, watch readability"
    else:
        band = "human-like band"
    return {
        "sentences": n,
        "mean_len": round(mean, 2),
        "std_len": round(sd, 2),
        "cv": round(cv, 3),
        "alternation": round(alt, 3),
        "min": min(lengths),
        "max": max(lengths),
        "band": band,
    }


def main():
    text = read_text(sys.argv[1] if len(sys.argv) > 1 else None)
    print(json.dumps(analyze(text), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
