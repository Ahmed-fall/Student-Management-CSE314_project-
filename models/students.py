from core.base_model import BaseModel

class Student(BaseModel):
    """
    Represents a Student entity.

    Strict OOP Implementation:
    - Inheritance: Inherits from BaseModel.
    - Encapsulation: All attributes are private (_var) with public properties.
    - Validation: Setters enforce type and value constraints immediately.
    """

    def __init__(self, id: int, user_id: int, level: int, birthdate: str, major: str):
        """
        Initialize and VALIDATE all data immediately.
        """
        self.id = id
        self.user_id = user_id
        self.level = level
        self.birthdate = birthdate
        self.major = major

    # ---------------------------------------------------------
    # Getters
    # ---------------------------------------------------------

    @property
    def id(self):
        return self._id

    @property
    def user_id(self):
        return self._user_id

    @property
    def level(self):
        return self._level

    @property
    def birthdate(self):
        return self._birthdate

    @property
    def major(self):
        return self._major

    # ---------------------------------------------------------
    # Setters (Validation Logic)
    # ---------------------------------------------------------

    @id.setter
    def id(self, value):
        if not isinstance(value, int):
            raise TypeError(f"Student ID must be an integer, got {type(value).__name__}")
        self._id = value

    @user_id.setter
    def user_id(self, value):
        if not isinstance(value, int):
            raise TypeError(f"User ID must be an integer, got {type(value).__name__}")
        self._user_id = value

    @level.setter
    def level(self, value):
        if not isinstance(value, int):
            raise TypeError(f"Level must be an integer, got {type(value).__name__}")
        
        if value <= 0:
            raise ValueError("Level must be greater than 0.")
        
        self._level = value

    @birthdate.setter
    def birthdate(self, value):
        if not isinstance(value, str):
            raise TypeError("Birthdate must be a string.")
        
        cleaned_birthdate = value.strip()
        if not cleaned_birthdate:
            raise ValueError("Birthdate cannot be empty.")
        
        self._birthdate = cleaned_birthdate

    @major.setter
    def major(self, value):
        if value is None:
            self._major = ""
        else:
            self._major = str(value).strip()

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
            "user_id": self._user_id,
            "level": self._level,
            "birthdate": self._birthdate,
            "major": self._major
        }

    @staticmethod
    def from_row(row):
        """
        Factory method to create a Student from a database row.
        """
        if not row:
            return None

        return Student(
            id=row["id"],
            user_id=row["user_id"],
            level=row["level"],
            birthdate=row["birthdate"],
            major=row["major"]
        )
