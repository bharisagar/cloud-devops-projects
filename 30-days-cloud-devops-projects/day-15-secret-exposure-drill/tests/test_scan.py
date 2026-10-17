import unittest

from scan import markdown, scan_text


class ScanTests(unittest.TestCase):
    def test_literal_is_reported_without_value(self):
        report = scan_text("PASSWORD=example-fake-password-123")
        self.assertEqual(report["decision"], "BLOCK AND TRIAGE")
        self.assertEqual(report["findings"][0]["line"], 1)
        self.assertNotIn("example-fake-password-123", str(report))
        self.assertNotIn("example-fake-password-123", markdown(report))

    def test_references_and_comments_are_not_flagged(self):
        report = scan_text("# PASSWORD=fake\nTOKEN=${TOKEN_FROM_ENV}\nAPI_KEY=process.env.API_KEY\n")
        self.assertEqual(report["findings"], [])

    def test_private_key_marker_is_critical(self):
        report = scan_text("-----BEGIN PRIVATE KEY-----")
        self.assertEqual(report["findings"][0]["severity"], "critical")

    def test_line_numbers_and_score(self):
        report = scan_text("SERVICE=demo\nTOKEN=example-fake-token\nPASSWORD=example-fake-pass\n")
        self.assertEqual([item["line"] for item in report["findings"]], [2, 3])
        self.assertEqual(report["risk_score"], 40)


if __name__ == "__main__":
    unittest.main()
