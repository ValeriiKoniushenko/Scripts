import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from scripts.ci.gitea import check_valgrind, run_game_valgrind  # noqa: E402
from scripts.ci.gitea.gitea_client import classified_review_body  # noqa: E402


class ReviewClassificationTests(unittest.TestCase):
    def test_classification_banners_are_first(self):
        expected = {
            "error": "❗ **— this check fails the build.**",
            "warning": "⚠️ **— this finding does not fail the build.**",
            "info": "ℹ️ **— this comment is informational.**",
        }
        for classification, prefix in expected.items():
            with self.subTest(classification=classification):
                self.assertTrue(
                    classified_review_body("details", classification).startswith(prefix)
                )

    def test_unknown_classification_is_rejected(self):
        with self.assertRaises(ValueError):
            classified_review_body("details", "unknown")

    def test_unit_test_valgrind_failure_starts_with_error(self):
        result = check_valgrind.ValgrindResult(["valgrind"], 42, "", "failure")
        self.assertTrue(
            check_valgrind.failure_review_body(result).startswith(
                "❗ **— this check fails the build.**"
            )
        )

    def test_game_valgrind_failure_starts_with_error(self):
        result = run_game_valgrind.ValgrindGameResult(
            ["valgrind"], 42, "", "ERROR SUMMARY: 1 errors", 5
        )
        self.assertTrue(
            run_game_valgrind.review_body("TemplateGame", result).startswith(
                "❗ **— this check fails the build.**"
            )
        )


if __name__ == "__main__":
    unittest.main()
