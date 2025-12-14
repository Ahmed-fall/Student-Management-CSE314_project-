from core.base_model import BaseModel

class Course(BaseModel):
    """
    Represents a Course entity.

    Strict OOP Implementation:
    - Inheritance: Inherits from BaseModel.
    - Encapsulation: All attributes are private (_var) with public properties.
    - Validation: Setters enforce type and value constraints immediately.
    """

    def __init__(
        self,id: int,
        code: str,
        name: str,
        description: str,
        credits: int,
        semester: str,
        max_students: int,
        instructor_id: int
    ):
        """
        Initialize and VALIDATE all data immediately.
        Setters are used to ensure validation logic runs at creation time.
        """

        # 1. IDs
        self.id = id
        self.instructor_id = instructor_id

        # 2. Core Course Data
        self.code = code
        self.name = name
        self.description = description
        self.credits = credits
        self.semester = semester
        self.max_students = max_students

    # ---------------------------------------------------------
    # Getters (@property)
    # ---------------------------------------------------------

    @property
    def id(self):
        return self._id

    @property
    def code(self):
        return self._code

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def credits(self):
        return self._credits

    @property
    def semester(self):
        return self._semester

    @property
    def max_students(self):
        return self._max_students

    @property
    def instructor_id(self):
        return self._instructor_id

    # ---------------------------------------------------------
    # Setters (Validation Logic)
    # ---------------------------------------------------------

    @id.setter
    def id(self, value):
        if not isinstance(value, int):
            raise TypeError(f"Course ID must be an integer, got {type(value).__name__}")
        self._id = value

    @code.setter
    def code(self, value):
        if not isinstance(value, str):
            raise TypeError("Course code must be a string.")

        cleaned_code = value.strip().upper()
        if not cleaned_code:
            raise ValueError("Course code cannot be empty.")

        self._code = cleaned_code

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError("Course name must be a string.")

        cleaned_name = value.strip()
        if not cleaned_name:
            raise ValueError("Course name cannot be empty.")

        self._name = cleaned_name

    @description.setter
    def description(self, value):
        # Allow NULL values safely
        if value is None:
            self._description = ""
        else:
            self._description = str(value).strip()

    @credits.setter
    def credits(self, value):
        if not isinstance(value, int):
            raise TypeError("Credits must be an integer.")

        if value <= 0:
            raise ValueError("Credits must be greater than 0.")

        self._credits = value

    @semester.setter
    def semester(self, value):
        if not isinstance(value, str):
            raise TypeError("Semester must be a string.")

        cleaned_semester = value.strip()
        if not cleaned_semester:
            raise ValueError("Semester cannot be empty.")

        self._semester = cleaned_semester

    @max_students.setter
    def max_students(self, value):
        if not isinstance(value, int):
            raise TypeError("Max students must be an integer.")

        if value <= 0:
            raise ValueError("Max students must be greater than 0.")

        self._max_students = value

    @instructor_id.setter
    def instructor_id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("Instructor ID must be an integer or None.")

        self._instructor_id = value

    # ---------------------------------------------------------
    # Polymorphism (Required by BaseModel)
    # ---------------------------------------------------------

    def to_dict(self):
        """
        Converts the object to a dictionary.
        Matches database column names exactly.
        """
        return {
            "id": self._id,
            "code": self._code,
            "name": self._name,
            "description": self._description,
            "credits": self._credits,
            "semester": self._semester,
            "max_students": self._max_students,
            "instructor_id": self._instructor_id
        }

    @staticmethod
    def from_row(row):
        """
        Factory method to create a Course from a database row.
        """
        if not row:
            return None

        return Course(
            id=row["id"],
            code=row["code"],
            name=row["name"],
            description=row["description"],
            credits=row["credits"],
            semester=row["semester"],
            max_students=row["max_students"],
            instructor_id=row["instructor_id"]
        )
