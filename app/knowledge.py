"""
Knowledge providers.

A knowledge provider gives the assistant access to documents without
requiring the rest of the application to know where those documents live.
"""

from pathlib import Path
from typing import Protocol

from google.api_core.exceptions import NotFound
from google.cloud import storage


class KnowledgeProvider(Protocol):
    """Interface implemented by every knowledge provider."""

    def list_documents(self) -> list[str]:
        """Return the available Markdown documents."""
        ...

    def read_document(self, filename: str) -> str:
        """Return the contents of one Markdown document."""
        ...


class LocalKnowledgeProvider:
    """Read Markdown documents from a local directory."""

    def __init__(self, knowledge_directory: Path):
        self.knowledge_directory = knowledge_directory

    def list_documents(self) -> list[str]:
        """Return all local Markdown document names."""

        if not self.knowledge_directory.exists():
            raise FileNotFoundError(
                f"Knowledge directory not found: "
                f"{self.knowledge_directory}"
            )

        return sorted(
            file.name
            for file in self.knowledge_directory.glob("*.md")
            if file.is_file()
        )

    def read_document(self, filename: str) -> str:
        """Read one local Markdown document."""

        if not filename.strip():
            raise ValueError("The filename cannot be empty.")

        path = self.knowledge_directory / filename

        if not path.exists() or not path.is_file():
            raise FileNotFoundError(filename)

        return path.read_text(encoding="utf-8")


class CloudKnowledgeProvider:
    """Read Markdown documents from a Google Cloud Storage bucket."""

    def __init__(
        self,
        bucket_name: str,
        project_id: str | None = None,
        client: storage.Client | None = None,
    ):
        if not bucket_name.strip():
            raise ValueError("The Cloud Storage bucket name is required.")

        self.bucket_name = bucket_name
        self.client = client or storage.Client(project=project_id)
        self.bucket = self.client.bucket(bucket_name)

    def list_documents(self) -> list[str]:
        """Return all Markdown object names from the bucket."""

        blobs = self.client.list_blobs(self.bucket_name)

        return sorted(
            blob.name
            for blob in blobs
            if blob.name.endswith(".md")
        )

    def read_document(self, filename: str) -> str:
        """Download one Markdown object as UTF-8 text."""

        if not filename.strip():
            raise ValueError("The filename cannot be empty.")

        blob = self.bucket.blob(filename)

        try:
            return blob.download_as_text(encoding="utf-8")
        except NotFound as error:
            raise FileNotFoundError(filename) from error