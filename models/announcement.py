# models/announcement.py

from core.base_model import BaseModel
import datetime

class Announcement(BaseModel):
    """
    Represents an Announcement entity.

    Strict OOP Implementation:
    - Inherits BaseModel.
    - Encapsulation: private attributes with getters/setters.
    - Validation: all input validated immediately.
    """

    def __init__(self, id, course_id, title, message, created_at=None):
        self.id = id
        self.course_id = course_id
        self.title = title
        self.message = message
        self.created_at = created_at or datetime.datetime.now().isoformat()

    # -------------------
    # Getters
    # -------------------
    @property
    def id(self):
        return self._id

    @property
    def course_id(self):
        return self._course_id

    @property
    def title(self):
        return self._title

    @property
    def message(self):
        return self._message

    @property
    def created_at(self):
        return self._created_at

    # -------------------
    # Setters (with validation)
    # -------------------
    @id.setter
    def id(self, value):
        if not isinstance(value, int):
            raise TypeError("Announcement ID must be an integer.")
        self._id = value

    @course_id.setter
    def course_id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("Course ID must be an integer or None for global announcement.")
        self._course_id = value

    @title.setter
    def title(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Title must be a non-empty string.")
        self._title = value.strip()

    @message.setter
    def message(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Message must be a non-empty string.")
        self._message = value.strip()

    @created_at.setter
    def created_at(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("created_at must be a valid datetime string.")
        self._created_at = value.strip()

    # -------------------
    # Convert to dict
    # -------------------
    def to_dict(self):
        """
        Converts the object to a dictionary.
        Matches the database column names exactly.
        """
        return {
            "id": self._id,
            "course_id": self._course_id,
            "title": self._title,
            "message": self._message,
            "created_at": self._created_at
        }

    # -------------------
    # Create object from DB row
    # -------------------
    @staticmethod
    def from_row(row):
        """
        Factory method to create an Announcement from a database row.
        Ensures compatibility with repository methods.
        """
        if row is None:
            return None
        return Announcement(
            id=row["id"],
            course_id=row["course_id"],
            title=row["title"],
            message=row["message"],
            created_at=row["created_at"]
        )
