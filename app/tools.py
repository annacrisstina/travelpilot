"""
Tools available to TravelPilot.

The tools access a travel knowledge base stored locally or in
Google Cloud Storage.
"""

from app.knowledge import KnowledgeProvider


class AssistantTools:
    """Operations that the AI agent can perform on the travel knowledge base."""

    def __init__(self, knowledge_provider: KnowledgeProvider):
        self.knowledge = knowledge_provider

    def list_documents(self) -> dict:
        """
        List the available travel knowledge documents.

        Use this tool when the user asks what travel information,
        destinations, topics or travel documents are available.

        Returns:
            A dictionary containing the operation status and filenames.
        """
        documents = self.knowledge.list_documents()

        return {
            "status": "success",
            "documents": documents,
            "document_count": len(documents),
        }

    def read_document(self, filename: str) -> dict:
        """
        Read a specific document from the travel knowledge base.

        Use this tool when the user asks about the contents of a known
        travel document or when another tool identifies a relevant filename.

        Args:
            filename: Exact Markdown filename, such as "rome.md".

        Returns:
            A dictionary containing the document content or an error.
        """
        try:
            content = self.knowledge.read_document(filename)
        except FileNotFoundError:
            return {
                "status": "error",
                "filename": filename,
                "error_message": f"Document '{filename}' was not found.",
            }

        return {
            "status": "success",
            "filename": filename,
            "content": content,
        }

    def search_documents(self, keyword: str) -> dict:
        """
        Search all travel knowledge documents and return short matching excerpts.

        Use this tool when the user asks which travel documents mention
        a specific destination, attraction or travel-related topic.

        Args:
            keyword: Word or phrase to search for, such as "Colosseum".

        Returns:
            A dictionary containing matching filenames and line excerpts.
        """
        normalized_keyword = keyword.strip().casefold()

        if not normalized_keyword:
            return {
                "status": "error",
                "keyword": keyword,
                "error_message": "The search keyword cannot be empty.",
            }

        matches: list[dict] = []

        for filename in self.knowledge.list_documents():
            content = self.knowledge.read_document(filename)
            excerpts: list[dict] = []

            for line_number, line in enumerate(content.splitlines(), start=1):
                if normalized_keyword in line.casefold():
                    excerpts.append(
                        {
                            "line_number": line_number,
                            "text": line.strip(),
                        }
                    )

                if len(excerpts) == 3:
                    break

            if excerpts:
                matches.append(
                    {
                        "filename": filename,
                        "excerpts": excerpts,
                    }
                )

        return {
            "status": "success",
            "keyword": keyword,
            "matches": matches,
            "match_count": len(matches),
        }

    def plan_trip(
        self,
        destination: str,
        days: int,
        interests: str = "",
        budget: str = "medium",
    ) -> dict:
        """
        Generate a personalized travel itinerary using the travel
        knowledge base.

        Args:
            destination: Destination city (e.g. "Rome").
            days: Number of travel days.
            interests: Optional travel interests.
            budget: Budget level ("low", "medium", "high").

        Returns:
            A dictionary containing the destination guide and
            planning instructions for the AI model.
        """

        if days < 1:
            return {
                "status": "error",
                "error_message": "The number of travel days must be at least 1.",
            }

        if budget not in {"low", "medium", "high"}:
            return {
                "status": "error",
                "error_message": (
                    "Budget must be one of: low, medium or high."
                ),
            }
        if days > 30:
            return {
                "status": "error",
                "error_message": (
                    "The maximum supported itinerary length is 30 days."
                ),
            }
        
        filename = (
            destination.strip()
            .lower()
            .replace(" ", "_")
            + ".md"
        )

        try:
            destination_guide = self.knowledge.read_document(filename)
        except FileNotFoundError:
            return {
                "status": "error",
                "destination": destination,
                "error_message": (
                    f"No travel guide is available for '{destination}'."
                ),
            }

        return {
            "status": "success",
            "destination": destination.title(),
            "days": days,
            "budget": budget,
            "interests": interests,
            "destination_guide": destination_guide,
            "instructions": (
                f"Create a personalized {days}-day itinerary for "
                f"{destination.title()} using ONLY the provided "
                f"destination guide. Consider the user's interests "
                f"('{interests}') and budget level ('{budget}'). "
                "Organize attractions day by day, recommend local "
                "food when appropriate, include transportation "
                "suggestions and finish with practical travel tips."
            ),
        }
