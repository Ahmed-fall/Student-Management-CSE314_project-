from core.base_model import BaseModel

class Submission(BaseModel):
    """
    Represents a Student's Submission entity.
    
    Strict OOP Implementation:
    - Inheritance: Inherits from BaseModel.
    - Encapsulation: All attributes are private (_var) with public properties.
    - Validation: Setters enforce type and value constraints immediately.
    """

    def __init__(self, id: int, assignment_id: int, student_id: int, content: str, submitted_at: str):
        """
        Initialize and VALIDATE all data immediately.
        We use self.variable = value (the setter) instead of self._variable = value
        to ensure validation logic runs during object creation.
        """
        # 1. IDs (Read-only context mostly, but type checked)
        self.id = id
        self.assignment_id = assignment_id
        self.student_id = student_id

        # 2. Content (Strict validation)
        self.content = content          # Cannot be empty
        self.submitted_at = submitted_at # Cannot be empty (Timestamp)

    # ---------------------------------------------------------
    # Getters (@property) - Explicitly exposing private data
    # ---------------------------------------------------------

    @property
    def id(self):
        return self._id

    @property
    def assignment_id(self):
        return self._assignment_id

    @property
    def student_id(self):
        return self._student_id

    @property
    def content(self):
        return self._content

    @property
    def submitted_at(self):
        return self._submitted_at

    # ---------------------------------------------------------
    # Setters (Validation Logic) - The Guard Rails
    # ---------------------------------------------------------

    @id.setter
    def id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError(f"Submission ID must be an integer, got {type(value).__name__}")
        self._id = value

    @assignment_id.setter
    def assignment_id(self, value):
        if not isinstance(value, int):
            raise TypeError(f"Assignment ID must be an integer, got {type(value).__name__}")
        self._assignment_id = value

    @student_id.setter
    def student_id(self, value):
        if not isinstance(value, int):
            raise TypeError(f"Student ID must be an integer, got {type(value).__name__}")
        self._student_id = value

    @content.setter
    def content(self, value):
        if not isinstance(value, str):
            raise TypeError("Submission content must be a string.")
        
        cleaned_content = value.strip()
        if not cleaned_content:
            raise ValueError("Submission content cannot be empty.")
        
        self._content = cleaned_content

    @submitted_at.setter
    def submitted_at(self, value):
        # We ensure the timestamp exists and is a string.
        # (Detailed date format validation happens in Service/Utils, but we ensure string existence here)
        if not isinstance(value, str):
            raise TypeError("Submitted_at timestamp must be a string.")
        
        cleaned_date = value.strip()
        if not cleaned_date:
            raise ValueError("Submission timestamp (submitted_at) is required.")
        
        self._submitted_at = cleaned_date

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
            "assignment_id": self._assignment_id,
            "student_id": self._student_id,
            "content": self._content,
            "submitted_at": self._submitted_at
        }
    
    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Submission(
            id=row['id'],
            assignment_id=row['assignment_id'],
            student_id=row['student_id'],
            content=row['content'],
            submitted_at=row['submitted_at']
        )