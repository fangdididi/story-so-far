import json, os, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import storybrief as sb

def ex(n):
    with open(os.path.join(ROOT, "examples", n), encoding="utf-8") as f:
        return json.load(f)

class T(unittest.TestCase):
    def test_examples_clean(self):
        for n in ("story-day1.json", "story-day8.json"):
            e, _ = sb.lint(ex(n)); self.assertEqual(e, [], n)
    def test_echo_warning(self):
        _, w = sb.lint(ex("story-day1.json")); self.assertTrue(any(x.startswith("W01 claim c2") for x in w))
    def test_echoes_cannot_confirm(self):
        s = ex("story-day1.json"); s["claims"][1]["status"] = "CONFIRMED"
        e, _ = sb.lint(s); self.assertTrue(any(x.startswith("L03 claim c2") for x in e))
    def test_party_cannot_confirm_itself(self):
        s = ex("story-day1.json"); s["claims"][2]["status"] = "CONFIRMED"
        e, _ = sb.lint(s); self.assertTrue(any(x.startswith("L03 claim c3") for x in e))
    def test_two_independent_reports_confirm(self):
        s = ex("story-day1.json")
        s["sources"] += [{"id": "r1", "layer": "reporting", "who": "A", "url": "u1", "own_access": True},
                         {"id": "r2", "layer": "reporting", "who": "B", "url": "u2", "own_access": True}]
        s["claims"].append({"id": "c9", "text": "x", "status": "CONFIRMED", "sources": ["r1", "r2"]})
        e, _ = sb.lint(s); self.assertEqual(e, [])
        s["sources"][-1]["echo_of"] = "r1"
        e, _ = sb.lint(s); self.assertTrue(any(x.startswith("L03 claim c9") for x in e))
    def test_market_is_not_evidence(self):
        s = ex("story-day1.json")
        s["claims"].append({"id": "c9", "text": "x", "status": "REPORTED", "sources": ["s6"]})
        e, _ = sb.lint(s); self.assertTrue(any(x.startswith("L10") for x in e))
    def test_retracted_needs_correction(self):
        s = ex("story-day1.json"); s["claims"][0]["status"] = "RETRACTED"
        e, _ = sb.lint(s); self.assertTrue(any(x.startswith("L07") for x in e))
    def test_heat_needs_fetch_time(self):
        s = ex("story-day1.json"); del s["heat"][0]["fetched_at"]
        e, _ = sb.lint(s); self.assertTrue(any(x.startswith("H01") for x in e))
    def test_cli_render_and_diff(self):
        py = sys.executable; sc = os.path.join(ROOT, "scripts", "storybrief.py")
        d1 = os.path.join(ROOT, "examples", "story-day1.json"); d8 = os.path.join(ROOT, "examples", "story-day8.json")
        r = subprocess.run([py, sc, "render", d8, "--lang", "zh"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0); self.assertIn("站得住的", r.stdout)
        r = subprocess.run([py, sc, "diff", d1, d8], capture_output=True, text=True)
        self.assertIn("MOVED    c2 RUMOR -> SUPERSEDED", r.stdout); self.assertIn("NEW      c4", r.stdout)
    def test_new_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(sb.cmd_new(t, "x"), 0); self.assertEqual(sb.cmd_new(t, "x"), 2)
            e, _ = sb.lint(json.load(open(os.path.join(t, "story.json"))))
            self.assertTrue(any(x.startswith("C03") for x in e))

if __name__ == "__main__":
    unittest.main()
