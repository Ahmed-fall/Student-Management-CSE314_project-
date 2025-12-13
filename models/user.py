from core.base_model import BaseModel 

class User(BaseModel): 

    
    def __init__(self, id, username, name, email, gender, role, password_hash=None):

        self.id = id
        self._password_hash = password_hash 
        self.username = username
        self.name = name
        self.email = email
        self.gender = gender
        self.role = role

    
    @property
    def id(self):
        return self._id

    @property
    def username(self):
        return self._username

    @property
    def name(self):
        return self._name

    @property
    def email(self):
        return self._email

    @property
    def gender(self):
        return self._gender

    @property
    def role(self):
        return self._role

    @id.setter
    def id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("User ID must be an integer.")
        self._id = value

    @username.setter
    def username(self, value):
        if not isinstance(value, str):
            raise TypeError("Username must be a string.")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Username cannot be empty.")
        self._username = cleaned

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError("Name must be a string.")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Name cannot be empty.")
        self._name = cleaned

    @email.setter
    def email(self, value):
        if not isinstance(value, str):
            raise TypeError("Email must be a string.")
        cleaned = value.strip()
        if "@" not in cleaned or "." not in cleaned:
            raise ValueError("Email format is invalid.")
        self._email = cleaned

    @gender.setter
    def gender(self, value):
        if value is not None and not isinstance(value, str):
            raise TypeError("Gender must be a string or None.")
        self._gender = value.strip().capitalize() if value else None

    @role.setter
    def role(self, value):
        ALLOWED_ROLES = {"student", "instructor", "admin"}
        if not isinstance(value, str) or value.lower() not in ALLOWED_ROLES:
            raise ValueError(f"Invalid role: {value}. Must be one of {ALLOWED_ROLES}.")
        self._role = value.lower()


    def to_dict(self):
        return {
            'id': self._id,
            'Username': self._username,
            'Name': self._name,
            'Email': self._email,
            'Gender': self._gender,
            'Role': self._role
        }

    @staticmethod
    def from_row(row):
        if not row:
            return None
        
        return User(
            id=row['id'],
            username=row['username'],
            name=row['name'],
            email=row['email'],
            gender=row['gender'],
            password_hash=row['password'], 
            role=row['role']
        )