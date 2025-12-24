from .user import User 

class Instructor(User):
    """
    Derived class demonstrating Inheritance from User.
    Holds instructor-specific profile data from the 'instructors' table.
    """
    
    def __init__(self, id, username, name, email, gender, role, password_hash, department,
                 instructor_profile_id=None, user_id_fk=None):
        
        # 1. Inheritance: Call the parent User constructor
        super().__init__(id, username, name, email, gender, role, password_hash)
        
        # 2. Instructor-specific profile attributes (Validation enforced by setters)
        self.instructor_profile_id = instructor_profile_id 
        self.user_id_fk = user_id_fk                 
        self.department = department

    # --- Getters (@property) --- 
    
    @property
    def instructor_profile_id(self):
        return self._instructor_profile_id

    @property
    def user_id_fk(self):
        return self._user_id_fk

    @property
    def department(self):
        return self._department

    # --- Setters (Validation Logic) ---
    
    @instructor_profile_id.setter
    def instructor_profile_id(self, value):
        if value is not None and not isinstance(value, int):
             raise TypeError("Instructor Profile ID must be an integer.")
        self._instructor_profile_id = value
        
    @user_id_fk.setter
    def user_id_fk(self, value):
        if value is not None and not isinstance(value, int):
             raise TypeError("User Foreign Key must be an integer.")
        self._user_id_fk = value

    @department.setter
    def department(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Department cannot be empty.")
        self._department = value.strip()

    # ---------------------------------------------------------
    # Polymorphism & Abstraction (Overrides and Required Methods)
    # ---------------------------------------------------------



    def to_dict(self):
        """REQUIRED: Combines User data and Instructor data for UI display."""
        data = super().to_dict()
        data.update({
            'instructor_profile_id': self.instructor_profile_id,
            'department': self.department
        })
        return data

    @staticmethod
    def from_row(row):
        """
        REQUIRED: Factory method to create Instructor object from a database JOIN row.
        """
        if not row:
            return None
        
        return Instructor(
            # User Data
            id=row['id'], 
            username=row['username'], 
            name=row['name'], 
            email=row['email'], 
            gender=row['gender'], 
            role=row['role'], 
            password_hash=row['password'],
            # Instructor Data
            department=row['department'],
            instructor_profile_id=row['instructor_profile_id'], 
            user_id_fk=row['user_id']
        )