from core.base_model import BaseModel
from datetime import datetime

class Submission(BaseModel):
    """
    Represents a Student's Submission entity.
    """

    ALLOWED_STATUSES = {"submitted", "graded", "late"}

    def __init__(self, id, assignment_id, student_id, content, submitted_at, grade=None, feedback=None, status="submitted"):
        # 1. IDs
        self.id = id
        self.assignment_id = assignment_id
        self.student_id = student_id

        # 2. Content
        self.content = content          
        self.submitted_at = submitted_at 

        # 3. Grading & Status (Now fully implemented)
        self.grade = grade
        self.feedback = feedback
        self.status = status

    # ---------------------------------------------------------
    # Getters
    # ---------------------------------------------------------
    @property
    def id(self): return self._id

    @property
    def assignment_id(self): return self._assignment_id

    @property
    def student_id(self): return self._student_id

    @property
    def content(self): return self._content

    @property
    def submitted_at(self): return self._submitted_at

    @property
    def grade(self): return self._grade

    @property
    def feedback(self): return self._feedback

    @property
    def status(self): return self._status

    # ---------------------------------------------------------
    # Setters (FIXED VALIDATION)
    # ---------------------------------------------------------
    @id.setter
    def id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("Submission ID must be an integer.")
        self._id = value

    @assignment_id.setter
    def assignment_id(self, value):
        if not isinstance(value, int):
            raise TypeError("Assignment ID must be an integer.")
        self._assignment_id = value

    @student_id.setter
    def student_id(self, value):
        if not isinstance(value, int):
            raise TypeError("Student ID must be an integer.")
        self._student_id = value

    @content.setter
    def content(self, value):
        if not isinstance(value, str):
            raise TypeError("Submission content must be a string.")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Submission content cannot be empty.")
        self._content = cleaned

    @submitted_at.setter
    def submitted_at(self, value):
        """
        FIX: Accepts both str and datetime objects.
        """
        if isinstance(value, datetime):
            self._submitted_at = value.isoformat()
        elif isinstance(value, str) and value.strip():
            self._submitted_at = value.strip()
        else:
            raise ValueError("Submitted_at must be a valid datetime object or string.")

    @grade.setter
    def grade(self, value):
        """
        Handles numeric grades or None (if not yet graded).
        """
        if value is None:
            self._grade = None
            return

        try:
            # Handle float, int, and PostgreSQL Decimal
            val = float(value)
            if val < 0:
                raise ValueError("Grade cannot be negative.")
            self._grade = val
        except (ValueError, TypeError):
             raise TypeError(f"Grade must be a number, got {type(value).__name__}")

    @feedback.setter
    def feedback(self, value):
        self._feedback = str(value).strip() if value else ""

    @status.setter
    def status(self, value):
        if not isinstance(value, str):
             raise TypeError("Status must be a string.")
        
        cleaned = value.lower().strip()
        if cleaned not in self.ALLOWED_STATUSES:
             # Optional: You can choose to just default to 'submitted' instead of crashing
             raise ValueError(f"Invalid status '{value}'. Allowed: {self.ALLOWED_STATUSES}")
        self._status = cleaned

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------
    def to_dict(self):
        return {
            "id": self._id,
            "assignment_id": self._assignment_id,
            "student_id": self._student_id,
            "submitted_at": self._submitted_at,
            "content": self._content,
            "grade": self._grade,
            "feedback": self._feedback,
            "status": self._status
        }
    
    @staticmethod
    def from_row(row):
        if not row: return None
        
        # Determine status dynamically if not present in row
        grade_val = row.get('grade_value')
        status = row.get('status')
        if not status:
             status = "graded" if grade_val is not None else "submitted"

        return Submission(
            id=row['id'],
            assignment_id=row['assignment_id'],
            student_id=row['student_id'],
            content=row['content'],
            submitted_at=row['submitted_at'],
            grade=grade_val,     
            feedback=row.get('feedback'),
            status=status
        )