"""Deterministic tests for the optional sepia-opt-* measure.py diagnostics.

Covers empty input, one sentence, Unicode punctuation, abbreviations, no final
punctuation, short texts, and each classification boundary. Also verifies the
scripts emit valid JSON and do not crash on valid UTF-8 input.

Standard library only:  python3 -m unittest discover -s tests
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BURST = ROOT / "skills" / "sepia-opt-burstiness" / "scripts" / "measure.py"
PERP = ROOT / "skills" / "sepia-opt-perplexity" / "scripts" / "measure.py"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


burst_measure = _load(str(BURST), "burst_measure")
perp_measure = _load(str(PERP), "perp_measure")


class BurstinessTests(unittest.TestCase):
    def test_empty_input(self):
        out = burst_measure.analyze("")
        self.assertIn("error", out)
        self.assertEqual(out["language_scope"], "english-prose-only")

    def test_one_sentence_is_too_few(self):
        out = burst_measure.analyze("One short sentence.")
        self.assertIn("error", out)
        self.assertIn(">=2 sentences", out["error"])

    def test_uniform_text_flagged(self):
        out = burst_measure.analyze("Word word. Word word. Word word.")
        self.assertEqual(out["band"], "uniform - low sentence-length variation")

    def test_highly_variable_text(self):
        text = (
            "Go. Go. Go. Go. Go. "
            "The quick brown fox jumps over the lazy dog near the riverbank "
            "while the children played happily outside."
        )
        out = burst_measure.analyze(text)
        self.assertIn("highly variable", out["band"])

    def test_mixed_text_moderate(self):
        out = burst_measure.analyze(
            "I went. The quick brown fox jumps over the lazy dog and then runs away fast."
        )
        self.assertEqual(out["band"], "moderate variation")
        self.assertEqual(out["language_scope"], "english-prose-only")

    def test_unicode_punctuation_no_crash(self):
        out = burst_measure.analyze("Café! \u201cQuotes?\u201d \u2014 em dash. R\u00e9sum\u00e9.")
        self.assertIn("sentences", out)

    def test_abbreviation_no_crash(self):
        out = burst_measure.analyze("Dr. Smith went to the U.S.A. He was happy.")
        self.assertIn("sentences", out)

    def test_no_final_punctuation(self):
        out = burst_measure.analyze("this is a sentence without ending")
        self.assertIn("error", out)


class PerplexityTests(unittest.TestCase):
    def test_empty_input(self):
        out = perp_measure.analyze("")
        self.assertIn("error", out)
        self.assertEqual(out["language_scope"], "english-prose-only")

    def test_single_token(self):
        out = perp_measure.analyze("Word.")
        self.assertEqual(out["tokens"], 1)
        self.assertIn("high lexical variety", out["band"])

    def test_low_variety_flagged(self):
        out = perp_measure.analyze("the the the the the the the the the the")
        self.assertIn("low lexical variety", out["band"])

    def test_high_variety_flagged(self):
        text = (
            "quartz zirconium xylophonist juxtaposition brackish wombat "
            "kleptomania zephyr quokka"
        )
        out = perp_measure.analyze(text)
        self.assertIn("high lexical variety", out["band"])

    def test_moderate_variety(self):
        out = perp_measure.analyze("The wizard cast a spell. The wizard found a spell book.")
        self.assertEqual(out["band"], "moderate lexical variety")
        self.assertEqual(out["language_scope"], "english-prose-only")

    def test_unicode_no_crash(self):
        out = perp_measure.analyze("Caf\u00e9 r\u00e9sum\u00e9 na\u00efve \u00fcber.")
        self.assertIn("tokens", out)

    def test_abbreviation_no_crash(self):
        out = perp_measure.analyze("Dr. Smith went to the U.S.A. happily.")
        self.assertIn("tokens", out)


class CliJsonTests(unittest.TestCase):
    def _run(self, script, text):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write(text)
            path = f.name
        try:
            return subprocess.run(
                [sys.executable, str(script), path],
                capture_output=True,
                text=True,
            )
        finally:
            Path(path).unlink(missing_ok=True)

    def test_burstiness_cli_emits_json(self):
        res = self._run(
            BURST,
            "I went. The quick brown fox jumps over the lazy dog and then runs away fast.",
        )
        self.assertEqual(res.returncode, 0, res.stderr)
        data = json.loads(res.stdout)
        self.assertIn("cv", data)

    def test_perplexity_cli_emits_json_on_utf8(self):
        res = self._run(PERP, "Caf\u00e9 r\u00e9sum\u00e9 na\u00efve \u00fcber. The quark zoomed past.")
        self.assertEqual(res.returncode, 0, res.stderr)
        data = json.loads(res.stdout)
        self.assertIn("ttr", data)

    def test_cli_handles_empty_file(self):
        res = self._run(BURST, "")
        self.assertEqual(res.returncode, 0, res.stderr)
        data = json.loads(res.stdout)
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
