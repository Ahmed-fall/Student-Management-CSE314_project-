from core.base_model import BaseModel

class Grade(BaseModel):
    """
    Represents a Grade entity for a Submission.
    
    Strict OOP Implementation:
    - Inheritance: Inherits from BaseModel.
    - Encapsulation: All attributes are private (_var) with public properties.
    - Validation: Setters enforce type and value constraints immediately.
    """

    def __init__(self, id: int, submission_id: int, grade_value: float, feedback: str):
        """
        Initialize and VALIDATE all data immediately.
        We use self.variable = value (the setter) instead of self._variable = value
        to ensure validation logic runs during object creation.
        """
        # 1. IDs (Read-only context mostly, but type checked)
        self.id = id
        self.submission_id = submission_id

        # 2. Grading Data (Strict validation)
        self.grade_value = grade_value  # Must be a number >= 0
        self.feedback = feedback        # Can be empty, sanitized to string

    # ---------------------------------------------------------
    # Getters (@property) - Explicitly exposing private data
    # ---------------------------------------------------------

    @property
    def id(self):
        return self._id

    @property
    def submission_id(self):
        return self._submission_id

    @property
    def grade_value(self):
        return self._grade_value

    @property
    def feedback(self):
        return self._feedback

    # ---------------------------------------------------------
    # Setters (Validation Logic) - The Guard Rails
    # ---------------------------------------------------------

    @id.setter
    def id(self, value):
        if not isinstance(value, int):
            raise TypeError(f"Grade ID must be an integer, got {type(value).__name__}")
        self._id = value

    @submission_id.setter
    def submission_id(self, value):
        if not isinstance(value, int):
            raise TypeError(f"Submission ID must be an integer, got {type(value).__name__}")
        self._submission_id = value

    @grade_value.setter
    def grade_value(self, value):
        # Allow int or float
        if not isinstance(value, (int, float)):
            raise TypeError(f"Grade value must be a number (int or float), got {type(value).__name__}")
        
        # Check constraints
        if value < 0:
            raise ValueError("Grade value cannot be negative.")
        
        self._grade_value = float(value)

    @feedback.setter
    def feedback(self, value):
        # Sanitization: Convert None to empty string to prevent UI errors
        if value is None:
            self._feedback = ""
        elif not isinstance(value, str):
             # Optional: Enforce strict string type if desired, or just stringify
             # Given strictness level, let's enforce string type but allow None above
             raise TypeError("Feedback must be a string.")
        else:
            self._feedback = value.strip()

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
            "submission_id": self._submission_id,
            "grade_value": self._grade_value,
            "feedback": self._feedback
        }

    @staticmethod
    def from_row(row):
        """
        Factory method to create a Grade from a database row.
        """
        if not row:
            return None
        return Grade(
            id=row['id'],
            submission_id=row['submission_id'],
            grade_value=row['grade_value'],
            feedback=row['feedback']
        )