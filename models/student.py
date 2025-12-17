from models.user import User

class Student(User):
    """
    Student model extending User.
    """

    def __init__(
        self,
        id, username, name, email, gender, password_hash,
        level, birthdate, major,
        user_id=None, # Made Optional for creation phase
        student_profile_id=None
    ):
        # 1. Initialize Parent
        super().__init__(
            id=id,
            username=username,
            name=name,
            email=email,
            gender=gender,
            role="student",
            password_hash=password_hash
        )

        # 2. Initialize Child
        self.user_id = user_id
        self.level = level
        self.birthdate = birthdate
        self.major = major
        self.student_profile_id = student_profile_id

    # --- Getters ---
    @property
    def user_id(self): return self._user_id

    @property
    def level(self): return self._level

    @property
    def birthdate(self): return self._birthdate

    @property
    def major(self): return self._major

    @property
    def student_profile_id(self): return self._student_profile_id

    # --- Setters ---
    @user_id.setter
    def user_id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("user_id must be an integer.")
        self._user_id = value

    @level.setter
    def level(self, value):
        if not isinstance(value, int):
            raise TypeError("level must be an integer.")
        if value <= 0:
            raise ValueError("level must be > 0.")
        self._level = value

    @birthdate.setter
    def birthdate(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("birthdate cannot be empty.")
        self._birthdate = value.strip()

    @major.setter
    def major(self, value):
        self._major = str(value).strip() if value else ""
    
    @student_profile_id.setter
    def student_profile_id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("student_profile_id must be an integer.")
        self._student_profile_id = value

    # --- Factories ---
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "user_id": self._user_id,
            "level": self._level,
            "birthdate": self._birthdate,
            "major": self._major,
            "student_profile_id": self._student_profile_id
        })
        return data

    @staticmethod
    def from_row(row):
        if not row: return None

        profile_id = row["student_profile_id"] if "student_profile_id" in row.keys() else None
        return Student(
            id=row["id"],
            username=row["username"],
            name=row["name"],
            email=row["email"],
            gender=row["gender"],
            password_hash=row["password"],
            user_id=row["user_id"],
            level=row["level"],
            birthdate=row["birthdate"],
            major=row["major"],
            student_profile_id=profile_id
        )