"""Tests for local and cloud knowledge providers."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock

from app.knowledge import (
    CloudKnowledgeProvider,
    LocalKnowledgeProvider,
)


class LocalKnowledgeProviderTests(unittest.TestCase):
    """Test the local filesystem knowledge provider."""

    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        self.knowledge_path = Path(self.temporary_directory.name)

        (self.knowledge_path / "day1.md").write_text(
            "# Day 1\n\nCompute Engine and VPC.",
            encoding="utf-8",
        )

        (self.knowledge_path / "day2.md").write_text(
            "# Day 2\n\nCloud Storage and Cloud SQL.",
            encoding="utf-8",
        )

        # This file must not appear in the Markdown document list.
        (self.knowledge_path / "notes.txt").write_text(
            "Not a Markdown document.",
            encoding="utf-8",
        )

        self.provider = LocalKnowledgeProvider(self.knowledge_path)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_list_documents_returns_only_markdown_files(self) -> None:
        self.assertEqual(
            self.provider.list_documents(),
            ["day1.md", "day2.md"],
        )

    def test_read_document_returns_contents(self) -> None:
        content = self.provider.read_document("day1.md")

        self.assertIn("Compute Engine", content)
        self.assertIn("VPC", content)

    def test_read_missing_document_raises_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.provider.read_document("missing.md")

    def test_empty_filename_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.provider.read_document("")


class CloudKnowledgeProviderTests(unittest.TestCase):
    """Test Cloud Storage behaviour with a mocked client."""

    def setUp(self) -> None:
        self.client = MagicMock()
        self.bucket = MagicMock()

        self.client.bucket.return_value = self.bucket

        self.provider = CloudKnowledgeProvider(
            bucket_name="test-knowledge-bucket",
            project_id="test-project",
            client=self.client,
        )

    def test_list_documents_filters_markdown_objects(self) -> None:
        markdown_blob = MagicMock()
        markdown_blob.name = "day1.md"

        nested_markdown_blob = MagicMock()
        nested_markdown_blob.name = "archive/day2.md"

        text_blob = MagicMock()
        text_blob.name = "notes.txt"

        self.client.list_blobs.return_value = [
            text_blob,
            nested_markdown_blob,
            markdown_blob,
        ]

        documents = self.provider.list_documents()

        self.assertEqual(
            documents,
            ["archive/day2.md", "day1.md"],
        )

        self.client.list_blobs.assert_called_once_with(
            "test-knowledge-bucket"
        )

    def test_read_document_downloads_utf8_text(self) -> None:
        blob = MagicMock()
        blob.download_as_text.return_value = (
            "# Day 3\n\nDocker and Kubernetes."
        )

        self.bucket.blob.return_value = blob

        content = self.provider.read_document("day3.md")

        self.assertIn("Docker", content)
        self.assertIn("Kubernetes", content)

        self.bucket.blob.assert_called_once_with("day3.md")
        blob.download_as_text.assert_called_once_with(
            encoding="utf-8"
        )


if __name__ == "__main__":
    unittest.main()