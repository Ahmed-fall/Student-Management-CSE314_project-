# models/user.py
from core.base_model import BaseModel 

class User(BaseModel): 
    """
    Base class for all users, inheriting from BaseModel.
    Implements Encapsulation using properties/setters and contains base validation.
    Matches schema: id, username, name, email, gender, password, role.
    """
    
    # 🌟 CORRECTION: ALLOWED_ROLES defined as a Class Constant 
    ALLOWED_ROLES = {"student", "instructor", "admin"} 
    
    def __init__(self, id, username, name, email, gender, role, password_hash=None):
        """Initializes and VALIDATES all data immediately using setters."""
        self.id = id
        self._password_hash = password_hash 
        self.username = username
        self.name = name
        self.email = email
        self.gender = gender
        self.role = role

    # --- Getters (@property) for Public Access ---
    
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
    
    @property
    def password_hash(self):
        return self._password_hash # Note: This getter is present in the provided source

    # --- Setters (Validation Logic) ---

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
        if not isinstance(value, str) or value.lower() not in User.ALLOWED_ROLES:
            raise ValueError(f"Invalid role: {value}. Must be one of {User.ALLOWED_ROLES}.")
        self._role = value.lower()

    # --- Abstraction (Required by BaseModel) ---

    def to_dict(self):
        """Returns dict for UI display with consistent, lowercase keys."""
        return {
            'id': self._id,
            'username': self._username,
            'name': self._name,
            'email': self._email,
            'gender': self._gender,
            'role': self._role
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
            role=row['role']
        )