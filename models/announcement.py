from core.base_model import BaseModel
from datetime import datetime

class Announcement(BaseModel):
    """
    Represents an Announcement entity.
    """

    def __init__(self, id, course_id, title, message, created_at=None):
        self.id = id
        self.course_id = course_id
        self.title = title
        self.message = message
        # Use current time if none provided
        self.created_at = created_at or datetime.now()

    # -------------------
    # Getters
    # -------------------
    @property
    def id(self): return self._id

    @property
    def course_id(self): return self._course_id

    @property
    def title(self): return self._title

    @property
    def message(self): return self._message

    @property
    def created_at(self): return self._created_at

    # -------------------
    # Setters (FIXED VALIDATION)
    # -------------------
    @id.setter
    def id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("Announcement ID must be an integer.")
        self._id = value

    @course_id.setter
    def course_id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("Course ID must be an integer.")
        self._course_id = value

    @title.setter
    def title(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Title must be a non-empty string.")
        self._title = value.strip()

    @message.setter
    def message(self, value):
        if value is None:
            self._message = "No details provided."
        else:
            self._message = str(value).strip() or "No details provided."

    @created_at.setter
    def created_at(self, value):
        """
        FIX: Accepts both str (from SQLite/JSON) AND datetime (from PostgreSQL).
        Stores as ISO format string.
        """
        if isinstance(value, datetime):
            self._created_at = value.isoformat()
        elif isinstance(value, str) and value.strip():
            self._created_at = value.strip()
        else:
            raise ValueError(f"created_at must be a valid datetime object or string. Got {type(value)}")

    # -------------------
    # Conversion
    # -------------------
    def to_dict(self):
        return {
            "id": self._id,
            "course_id": self._course_id,
            "title": self._title,
            "message": self._message,
            "created_at": self._created_at
        }

    @staticmethod
    def from_row(row):
        if row is None: return None
        return Announcement(
            id=row["id"],
            course_id=row["course_id"],
            title=row["title"],
            message=row["message"],
            created_at=row["created_at"]
        )