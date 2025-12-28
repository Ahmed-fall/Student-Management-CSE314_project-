from core.base_model import BaseModel

class Grade(BaseModel):
    """
    Represents a Grade entity for a Submission.
    """

    def __init__(self, id: int, submission_id: int, grade_value: float, feedback: str):
        # 1. IDs 
        self.id = id
        self.submission_id = submission_id

        # 2. Grading Data 
        self.grade_value = grade_value  
        self.feedback = feedback        

    # ---------------------------------------------------------
    # Getters
    # ---------------------------------------------------------
    @property
    def id(self): return self._id

    @property
    def submission_id(self): return self._submission_id

    @property
    def grade_value(self): return self._grade_value

    @property
    def feedback(self): return self._feedback

    # ---------------------------------------------------------
    # Setters
    # ---------------------------------------------------------
    @id.setter
    def id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("Grade ID must be an integer.")
        self._id = value

    @submission_id.setter
    def submission_id(self, value):
        if not isinstance(value, int):
            raise TypeError("Submission ID must be an integer.")
        self._submission_id = value

    @grade_value.setter
    def grade_value(self, value):
        """
        FIX: Handles int, float, and PostgreSQL Decimal types by converting to float.
        """
        try:
            val = float(value)
        except (ValueError, TypeError):
             raise TypeError(f"Grade value must be a number, got {type(value).__name__}")
        
        if val < 0:
            raise ValueError("Grade value cannot be negative.")
        
        self._grade_value = val

    @feedback.setter
    def feedback(self, value):
        if value is None:
            self._feedback = ""
        else:
            self._feedback = str(value).strip()

    # ---------------------------------------------------------
    # Conversion
    # ---------------------------------------------------------
    def to_dict(self):
        return {
            "id": self._id,
            "submission_id": self._submission_id,
            "grade_value": self._grade_value,
            "feedback": self._feedback
        }

    @staticmethod
    def from_row(row):
        if not row: return None
        return Grade(
            id=row['id'],
            submission_id=row['submission_id'],
            grade_value=row['grade_value'],
            feedback=row['feedback']
        )