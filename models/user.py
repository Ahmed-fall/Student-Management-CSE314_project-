from core.base_model import BaseModel
from datetime import datetime

class User(BaseModel): 
    """
    Base class for all users.
    Parent to Student and Instructor.
    """
    
    ALLOWED_ROLES = {"student", "instructor", "admin"} 
    ALLOWED_GENDERS = {"male", "female", "engineer"} 
    
    def __init__(self, id, username, name, email, gender, role, password_hash=None, created_at=None):
        self.id = id
        self.username = username
        self.name = name
        self.email = email
        self.gender = gender
        self.role = role
        
        # Internal state
        self._password_hash = password_hash
        
        self.created_at = created_at or datetime.now()

    # --- Getters ---
    
    @property
    def id(self): return self._id

    @property
    def username(self): return self._username

    @property
    def name(self): return self._name

    @property
    def email(self): return self._email

    @property
    def gender(self): return self._gender

    @property
    def role(self): return self._role
    
    @property
    def password_hash(self): return self._password_hash 

    @property
    def created_at(self): return self._created_at

    # --- Setters ---

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
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name cannot be empty.")
        self._name = value.strip()

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
        if not isinstance(value, str) or value.lower() not in self.ALLOWED_GENDERS:
            raise ValueError(f"Invalid gender: {value}. Must be {self.ALLOWED_GENDERS}")
        self._gender = value.lower()

    @role.setter
    def role(self, value):
        if not isinstance(value, str) or value.lower() not in self.ALLOWED_ROLES:
            raise ValueError(f"Invalid role: {value}. Must be {self.ALLOWED_ROLES}")
        self._role = value.lower()

    @created_at.setter
    def created_at(self, value):
        """
        FIX: Accepts both str and datetime objects.
        """
        if isinstance(value, datetime):
            self._created_at = value.isoformat()
        elif isinstance(value, str) and value.strip():
            self._created_at = value.strip()
        else:
            # Fallback or strict error - here we assume current time if invalid/None during init
            self._created_at = datetime.now().isoformat()

    # --- Abstraction ---

    def to_dict(self):
        """Returns dict for UI. Password is intentionally excluded for security."""
        return {
            'id': self._id,
            'username': self._username,
            'name': self._name,
            'email': self._email,
            'gender': self._gender,
            'role': self._role,
            'created_at': self._created_at
        }

    @staticmethod
    def from_row(row):
        """Factory method to create User from a database Row object."""
        if not row:
            return None
        
        return User(
            id=row['id'],
            username=row['username'],
            name=row['name'],
            email=row['email'],
            gender=row['gender'],
            password_hash=row['password'], 
            role=row['role'],
            created_at=row.get('created_at') # Pass safely
        )