"""Document entity - core domain object representing a document."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Document:
    """Domain entity representing a document in the system.
    
    Attributes:
        title: Document title.
        content: Document content/text.
        source: Source of the document (URL, file path, etc).
        date: When the document was created/extracted (defaults to now).
        tag: Optional tag for categorization.
        _id: MongoDB document ID (None if not yet persisted).
    """
    title: str
    content: str
    source: str
    date: datetime = field(default_factory=datetime.now)
    tag: Optional[str] = None
    _id: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert document to dictionary for persistence.
        
        Returns:
            Dictionary with all fields including formatted date.
        """
        data = asdict(self)
        # Format date for JSON serialization
        data['date'] = self.date.strftime("%Y-%m-%d %H:%M:%S")
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Document":
        """Create document from dictionary (e.g., from JSON).
        
        Args:
            data: Dictionary with document fields.
            
        Returns:
            Document instance.
        """
        # Parse date string
        date_str = data.get("date", "")
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            date = datetime.now()

        return cls(
            title=data["title"],
            content=data["content"],
            source=data["source"],
            date=date,
            tag=data.get("tag"),
            _id=data.get("_id"),
        )
