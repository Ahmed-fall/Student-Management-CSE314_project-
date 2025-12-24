from core.base_model import BaseModel

class Assignment(BaseModel):
    """
    Represents an Assignment entity.
    
    Strict OOP Implementation:
    - Inheritance: Inherits from BaseModel.
    - Encapsulation: All attributes are private (_var) with public properties.
    - Validation: Setters enforce type and value constraints immediately.
    """

    # Constant to enforce database constraints on 'type' column
    ALLOWED_TYPES = {"quiz", "project", "homework", "exam"}

    def __init__(self, id: int, course_id: int, title: str, description: str, type: str, due_date: str, max_score: int):
        """
        Initialize and VALIDATE all data immediately.
        We use self.variable = value (the setter) instead of self._variable = value
        to ensure validation logic runs during object creation.
        """
        # 1. IDs (Read-only context mostly, but type checked)
        self.id = id
        self.course_id = course_id

        # 2. Content (Strict validation)
        self.title = title
        self.description = description  # Can be empty
        self.type = type                # Must be 'quiz' or 'project'
        self.due_date = due_date        # Cannot be empty
        self.max_score = max_score      # Must be > 0

    # ---------------------------------------------------------
    # Getters (@property) - Explicitly exposing private data
    # ---------------------------------------------------------

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
    def description(self):
        return self._description

    @property
    def type(self):
        return self._type

    @property
    def due_date(self):
        return self._due_date

    @property
    def max_score(self):
        return self._max_score

    # ---------------------------------------------------------
    # Setters (Validation Logic) - The Guard Rails
    # ---------------------------------------------------------

    @id.setter
    def id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError(f"Assignment ID must be an integer, got {type(value).__name__}")
        self._id = value

    @course_id.setter
    def course_id(self, value):
        if not isinstance(value, int):
            raise TypeError(f"Course ID must be an integer, got {type(value).__name__}")
        self._course_id = value

    @title.setter
    def title(self, value):
        if not isinstance(value, str):
            raise TypeError("Title must be a string.")
        
        cleaned_title = value.strip()
        if not cleaned_title:
            raise ValueError("Assignment title cannot be empty.")
        
        self._title = cleaned_title

    @description.setter
    def description(self, value):
        # Sanitization: Convert None to empty string to prevent UI errors
        if value is None:
            self._description = ""
        else:
            self._description = str(value).strip()

    @type.setter
    def type(self, value):
        if not isinstance(value, str):
            raise TypeError("Type must be a string.")
        
        cleaned_type = value.lower().strip()
        
        if cleaned_type not in self.ALLOWED_TYPES:
            raise ValueError(f"Invalid assignment type '{value}'. Must be one of: {self.ALLOWED_TYPES}")
        
        self._type = cleaned_type

    @due_date.setter
    def due_date(self, value):
        if not isinstance(value, str):
            raise TypeError("Due date must be a string.")
        
        cleaned_date = value.strip()
        if not cleaned_date:
            raise ValueError("Due date cannot be empty.")
        
        self._due_date = cleaned_date

    @max_score.setter
    def max_score(self, value):
        if not isinstance(value, int):
            raise TypeError(f"Max score must be an integer, got {type(value).__name__}")
        
        if value <= 0:
            raise ValueError("Max score must be greater than 0.")
        
        self._max_score = value

    # ---------------------------------------------------------
    # Polymorphism (Required by BaseModel)
    # ---------------------------------------------------------
    def to_dict(self):
        """
        Converts the object to a dictionary for the UI.
        Matches the database column names exactly.
        """
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
        """
        Factory method to create an Assignment from a database row.
        Safe against optional fields and missing data.
        """
        if not row:
            return None
        
        return Assignment(
            id=row['id'],
            course_id=row['course_id'],
            title=row['title'],
            description=row['description'],
            type=row['type'],
            due_date=row['due_date'],
            max_score=row['max_score']
        )