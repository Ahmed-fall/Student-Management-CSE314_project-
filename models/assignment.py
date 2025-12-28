from core.base_model import BaseModel
from datetime import datetime

class Assignment(BaseModel):
    """
    Represents an Assignment entity.
    """

    ALLOWED_TYPES = {"quiz", "project", "homework", "exam"}

    def __init__(self, id: int, course_id: int, title: str, description: str, type: str, due_date, max_score: int):
        self.id = id
        self.course_id = course_id
        self.title = title
        self.description = description
        self.type = type
        self.due_date = due_date  # Validated by setter below
        self.max_score = max_score

    # ---------------------------------------------------------
    # Getters
    # ---------------------------------------------------------
    @property
    def id(self): return self._id

    @property
    def course_id(self): return self._course_id

    @property
    def title(self): return self._title

    @property
    def description(self): return self._description

    @property
    def type(self): return self._type

    @property
    def due_date(self): return self._due_date

    @property
    def max_score(self): return self._max_score

    # ---------------------------------------------------------
    # Setters (FIXED VALIDATION)
    # ---------------------------------------------------------
    @id.setter
    def id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("Assignment ID must be an integer.")
        self._id = value

    @course_id.setter
    def course_id(self, value):
        if not isinstance(value, int):
            raise TypeError("Course ID must be an integer.")
        self._course_id = value

    @title.setter
    def title(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Assignment title cannot be empty.")
        self._title = value.strip()

    @description.setter
    def description(self, value):
        self._description = str(value).strip() if value else ""

    @type.setter
    def type(self, value):
        if not isinstance(value, str):
            raise TypeError("Type must be a string.")
        cleaned = value.lower().strip()
        if cleaned not in self.ALLOWED_TYPES:
            raise ValueError(f"Invalid type '{value}'. Allowed: {self.ALLOWED_TYPES}")
        self._type = cleaned

    @due_date.setter
    def due_date(self, value):
        """
        FIX: Accepts both str and datetime.
        """
        if isinstance(value, datetime):
            self._due_date = value.isoformat()
        elif isinstance(value, str) and value.strip():
            self._due_date = value.strip()
        else:
            raise ValueError("Due date must be a valid datetime object or string.")

    @max_score.setter
    def max_score(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Max score must be an integer greater than 0.")
        self._max_score = value

    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------
    def to_dict(self):
        return {
            "id": self._id,
            "course_id": self._course_id,
            "title": self._title,
            "description": self._description,
            "type": self._type,
            "due_date": self._due_date,
            "max_score": self._max_score
        }

    @staticmethod
    def from_row(row):
        if not row: return None
        return Assignment(
            id=row['id'],
            course_id=row['course_id'],
            title=row['title'],
            description=row['description'],
            type=row['type'],
            due_date=row['due_date'],
            max_score=row['max_score']
        )