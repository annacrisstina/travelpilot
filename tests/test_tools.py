"""Tests for the assistant's knowledge tools."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from app.knowledge import LocalKnowledgeProvider
from app.tools import AssistantTools


class AssistantToolsTests(unittest.TestCase):
    """Test the tools using a temporary local knowledge base."""

    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        knowledge_path = Path(self.temporary_directory.name)

        (knowledge_path / "containers.md").write_text(
            "\n".join(
                [
                    "# Containers",
                    "",
                    "Docker packages applications into images.",
                    "Kubernetes orchestrates containers.",
                ]
            ),
            encoding="utf-8",
        )

        (knowledge_path / "storage.md").write_text(
            "\n".join(
                [
                    "# Storage",
                    "",
                    "Cloud Storage stores objects.",
                    "Cloud SQL provides relational databases.",
                ]
            ),
            encoding="utf-8",
        )

        provider = LocalKnowledgeProvider(knowledge_path)
        self.tools = AssistantTools(provider)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_list_documents_returns_structured_result(self) -> None:
        result = self.tools.list_documents()

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["document_count"], 2)
        self.assertEqual(
            result["documents"],
            ["containers.md", "storage.md"],
        )

    def test_read_document_returns_structured_result(self) -> None:
        result = self.tools.read_document("storage.md")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["filename"], "storage.md")
        self.assertIn("Cloud Storage", result["content"])

    def test_read_missing_document_returns_error(self) -> None:
        result = self.tools.read_document("missing.md")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["filename"], "missing.md")
        self.assertIn("not found", result["error_message"].lower())

    def test_search_returns_matching_excerpts(self) -> None:
        result = self.tools.search_documents("Docker")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["keyword"], "Docker")
        self.assertEqual(result["match_count"], 1)

        match = result["matches"][0]

        self.assertEqual(match["filename"], "containers.md")
        self.assertGreaterEqual(len(match["excerpts"]), 1)
        self.assertIn(
            "Docker",
            match["excerpts"][0]["text"],
        )
        self.assertIsInstance(
            match["excerpts"][0]["line_number"],
            int,
        )

    def test_search_is_case_insensitive(self) -> None:
        result = self.tools.search_documents("kubernetes")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["match_count"], 1)
        self.assertEqual(
            result["matches"][0]["filename"],
            "containers.md",
        )

    def test_search_with_no_matches_is_successful(self) -> None:
        result = self.tools.search_documents("Bigtable")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["match_count"], 0)
        self.assertEqual(result["matches"], [])

    def test_empty_search_returns_error(self) -> None:
        result = self.tools.search_documents("   ")

        self.assertEqual(result["status"], "error")
        self.assertIn(
            "cannot be empty",
            result["error_message"].lower(),
        )


if __name__ == "__main__":
    unittest.main()