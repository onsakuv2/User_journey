import importlib.util
import pathlib
import unittest


SCRIPT_PATH = pathlib.Path(__file__).resolve().parents[1] / "azure_boards_sync.py"
SPEC = importlib.util.spec_from_file_location("azure_boards_sync", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AzureBoardsSyncTests(unittest.TestCase):
    def test_normalize_title_collapses_case_and_whitespace(self):
        self.assertEqual(MODULE.normalize_title("  My   Story  "), "my story")

    def test_build_auth_header_uses_basic_prefix(self):
        header = MODULE.build_auth_header("token123")
        self.assertTrue(header.startswith("Basic "))

    def test_build_existing_index_keys_by_type_and_normalized_title(self):
        work_items = [
            {
                "id": 42,
                "fields": {
                    "System.WorkItemType": "Epic",
                    "System.Title": "Checkout Overhaul",
                },
            }
        ]
        index = MODULE.build_existing_index(work_items)
        self.assertIn(("Epic", "checkout overhaul"), index)

    def test_plan_publish_reuses_existing_items_and_nests_children(self):
        existing = MODULE.build_existing_index(
            [
                {
                    "id": 7,
                    "fields": {
                        "System.WorkItemType": "Epic",
                        "System.Title": "Platform Upgrade",
                    },
                }
            ]
        )
        planned = [
            {
                "type": "Epic",
                "title": "Platform Upgrade",
                "children": [
                    {
                        "type": "User Story",
                        "title": "Move authentication endpoints",
                    }
                ],
            }
        ]
        plan = MODULE.plan_publish(existing, planned)
        self.assertEqual(plan[0]["action"], "reuse")
        self.assertEqual(plan[0]["id"], 7)
        self.assertEqual(plan[1]["parent_id"], 7)
        self.assertEqual(plan[1]["action"], "create")


if __name__ == "__main__":
    unittest.main()