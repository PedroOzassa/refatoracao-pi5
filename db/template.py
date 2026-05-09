from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from bson import ObjectId

@dataclass
class Document:
    title: str
    content: str
    date: datetime
    tag: list[str]
    source: str
    _id: Optional[ObjectId] = field(default=None, repr=False)

    def to_dict(self) -> dict:
        doc = {
            "title": self.title,
            "content": self.content,
            "date": self.date,
            "tag": self.tag if isinstance(self.tag, list) else [self.tag],
            "source": self.source,
        }
        if self._id is not None:
            doc["_id"] = self._id
        return doc

    @staticmethod
    def from_dict(data: dict) -> "Document":
        return Document(
            title=data["title"],
            content=data["content"],
            date=data["date"],
            tag=data.get("tag", []),
            source=data["source"],
            _id=data.get("_id"),
        )
