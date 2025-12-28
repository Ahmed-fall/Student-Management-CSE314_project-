from core.base_model import BaseModel

class Course(BaseModel):
    """
    Represents a Course entity.
    """

    def __init__(
        self, id: int, code: str, name: str, description: str, 
        credits: int, semester: str, max_students: int, instructor_id: int
    ):
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
        
        # Internal state for dashboard
        self._enrolled_count = 0

    # ---------------------------------------------------------
    # Getters
    # ---------------------------------------------------------
    @property
    def id(self): return self._id

    @property
    def code(self): return self._code

    @property
    def name(self): return self._name

    @property
    def description(self): return self._description

    @property
    def credits(self): return self._credits

    @property
    def semester(self): return self._semester

    @property
    def max_students(self): return self._max_students

    @property
    def instructor_id(self): return self._instructor_id

    # [FIX] Added Property for Enrolled Count so Service can update it
    @property
    def enrolled_count(self):
        return self._enrolled_count

    # ---------------------------------------------------------
    # Setters
    # ---------------------------------------------------------
    @id.setter
    def id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("Course ID must be an integer.")
        self._id = value

    @code.setter
    def code(self, value):
        if not isinstance(value, str):
            raise TypeError("Course code must be a string.")
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Course code cannot be empty.")
        self._code = cleaned

    @name.setter
    def name(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Course name cannot be empty.")
        self._name = value.strip()

    @description.setter
    def description(self, value):
        self._description = str(value).strip() if value else ""

    @credits.setter
    def credits(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Credits must be a positive integer.")
        self._credits = value

    @semester.setter
    def semester(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Semester cannot be empty.")
        self._semester = value.strip()

    @max_students.setter
    def max_students(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Max students must be a positive integer.")
        self._max_students = value

    @instructor_id.setter
    def instructor_id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("Instructor ID must be an integer.")
        self._instructor_id = value

    # [FIX] Added Setter so the Service can update the private variable
    @enrolled_count.setter
    def enrolled_count(self, value):
        if not isinstance(value, int):
            return # Ignore invalid updates
        self._enrolled_count = value

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------
    def to_dict(self):
        return {
            "id": self._id,
            "code": self._code,
            "name": self._name,
            "description": self._description,
            "credits": self._credits,
            "semester": self._semester,
            "max_students": self._max_students,
            "instructor_id": self._instructor_id,
            "enrolled_count": self._enrolled_count # Now correctly updated via setter
        }

    @staticmethod
    def from_row(row):
        if not row: return None
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