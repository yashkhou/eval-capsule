import unittest

from eval_capsule.core import evaluate_assertion


class AssertionDslTests(unittest.TestCase):
    def setUp(self):
        self.data = {"score": 0.93, "items": ["a", "b"], "meta": {"model/name": "gpt", "note": "ready-42"}}

    def test_numeric_regex_and_length_assertions(self):
        self.assertTrue(evaluate_assertion(self.data, {"path": "/score", "gte": 0.9, "lte": 1})["passed"])
        self.assertTrue(evaluate_assertion(self.data, {"path": "/items", "length": 2})["passed"])
        self.assertTrue(evaluate_assertion(self.data, {"path": "/meta/note", "matches": r"ready-\d+"})["passed"])

    def test_json_pointer_escaping(self):
        result = evaluate_assertion(self.data, {"path": "/meta/model~1name", "equals": "gpt"})
        self.assertTrue(result["passed"])

    def test_missing_path_becomes_failed_assertion_not_exception(self):
        result = evaluate_assertion(self.data, {"path": "/missing", "equals": 1})
        self.assertFalse(result["passed"])
        self.assertEqual(result["error"], "path does not exist")
        self.assertTrue(evaluate_assertion(self.data, {"path": "/missing", "exists": False})["passed"])


if __name__ == "__main__":
    unittest.main()
