from core.base_model import BaseModel

class Enrollment(BaseModel):
    """
    Represents an Enrollment entity.

    Strict OOP Implementation:
    - Inheritance: Inherits from BaseModel.
    - Encapsulation: All attributes are private (_var) with public properties.
    - Validation: Setters enforce type and value constraints immediately.
    """

    # Enforced by DB design
    ALLOWED_STATUS = {"enrolled", "dropped"}

    def __init__(
        self,
        id: int,
        student_id: int,
        course_id: int,
        date_enrolled: str,
        status: str
    ):
        """
        Initialize and VALIDATE all data immediately.
        """

        # 1. IDs
        self.id = id
        self.student_id = student_id
        self.course_id = course_id

        # 2. Enrollment Info
        self.date_enrolled = date_enrolled
        self.status = status

    # ---------------------------------------------------------
    # Getters (@property)
    # ---------------------------------------------------------

    @property
    def id(self):
        return self._id

    @property
    def student_id(self):
        return self._student_id

    @property
    def course_id(self):
        return self._course_id

    @property
    def date_enrolled(self):
        return self._date_enrolled

    @property
    def status(self):
        return self._status

    # ---------------------------------------------------------
    # Setters (Validation Logic)
    # ---------------------------------------------------------

    @id.setter
    def id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError(f"Enrollment ID must be an integer, got {type(value).__name__}")
        self._id = value

    @student_id.setter
    def student_id(self, value):
        if not isinstance(value, int):
            raise TypeError("Student ID must be an integer.")
        self._student_id = value

    @course_id.setter
    def course_id(self, value):
        if not isinstance(value, int):
            raise TypeError("Course ID must be an integer.")
        self._course_id = value

    @date_enrolled.setter
    def date_enrolled(self, value):
        if value is None:
            self._date_enrolled = None
            return

        if isinstance(value, str):
            self._date_enrolled = value.strip()
            return

        raise TypeError("date_enrolled must be a string or None.")


    @status.setter
    def status(self, value):
        if not isinstance(value, str):
            raise TypeError("Status must be a string.")

        cleaned_status = value.lower().strip()

        if cleaned_status not in self.ALLOWED_STATUS:
            raise ValueError(
                f"Invalid enrollment status '{value}'. "
                f"Must be one of: {self.ALLOWED_STATUS}"
            )

        self._status = cleaned_status

    # ---------------------------------------------------------
    # Polymorphism (Required by BaseModel)
    # ---------------------------------------------------------

    def to_dict(self):
        return {
            "id": self._id,
            "student_id": self._student_id,
            "course_id": self._course_id,
            "date_enrolled": self._date_enrolled,
            "status": self._status
        }


    @staticmethod
    def from_row(row):
        """
        Factory method to create an Enrollment from a database row.
        """
        if not row:
            return None

        return Enrollment(
            id=row["id"],
            student_id=row["student_id"],
            course_id=row["course_id"],
            date_enrolled=row["date_enrolled"],
            status=row["status"]
        )
