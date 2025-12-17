# services/auth_service.py
from core.base_service import BaseService
from repositories.user_repo import UserRepository
from repositories.student_repo import StudentRepository
from repositories.instructor_repo import InstructorRepository
from models.user import User
from models.student import Student
from models.instructor import Instructor

# Importing the security utility from the core directory
from core import security 

class AuthService(BaseService):
    """
    Handles identity verification (Authentication) and role-based permissions (Authorization).
    Coordinates logic across User, Student, and Instructor repositories.
    """

    def __init__(self):
        self.user_repo = UserRepository()
        self.student_repo = StudentRepository()
        self.instructor_repo = InstructorRepository()

    # ---------------------------------------------------------
    # 1. Authentication (Login)
    # ---------------------------------------------------------
    def login(self, identifier, password):
        """
        Verifies credentials and returns a polymorphic profile object.
        Checks both username and email for convenience.
        """
        try:
            # Step 1: Find user by username or email
            user_obj = self.user_repo.get_by_username(identifier) or \
                       self.user_repo.get_by_email(identifier)

            if not user_obj:
                return None 

            # Step 2: Verify password hash
            if not security.verify_password(password, user_obj.password_hash):
                return None 

            # Step 3: Return specific child model based on role
            if user_obj.role == "student":
                return self.student_repo.get_by_id(user_obj.id) 
            elif user_obj.role == "instructor":
                return self.instructor_repo.get_by_id(user_obj.id)
            
            return user_obj # Admin/Base User fallback

        except Exception as e:
            self.handle_db_error(e)

    # ---------------------------------------------------------
    # 2. Authorization (Access Control)
    # ---------------------------------------------------------
    def authorize_role(self, current_user: User, allowed_roles: list):
        """
        Enforces Role-Based Access Control (RBAC).
        """
        if current_user.role not in allowed_roles:
            raise PermissionError(f"Access Denied: Action requires one of {allowed_roles}.")

    # ---------------------------------------------------------
    # 3. Registration 
    # ---------------------------------------------------------
    def register(self, user_data: dict, profile_data: dict, role: str):
        """
        Coordinates the creation of a User and their specific profile atomically.
        If profile creation fails, it rolls back by deleting the User record.
        """
        try:
            # 1. Validate role against User constants
            if role not in User.ALLOWED_ROLES:
                raise ValueError(f"Invalid role. Must be one of {User.ALLOWED_ROLES}.")

            # 2. Security: Hash password before saving
            password_hash = security.hash_password(user_data['password'])

            # 3. Create base User object
            new_user = User(
                id=None,
                username=user_data['username'],
                name=user_data['name'],
                email=user_data['email'],
                gender=user_data['gender'],
                role=role,
                password_hash=password_hash
            )
            
            # Save User to DB and get the new ID
            created_user = self.user_repo.create(new_user)

            # 4. Create specialized profile
            try:
                if role == "student":
                    student = Student(
                        id=None, 
                        username=created_user.username, 
                        name=created_user.name,
                        email=created_user.email, 
                        gender=created_user.gender,
                        password_hash=password_hash, 
                        level=profile_data['level'],
                        birthdate=profile_data['birthdate'], 
                        major=profile_data['major'],
                        user_id=created_user.id
                    )
                    return self.student_repo.create(student)

                elif role == "instructor":
                    instructor = Instructor(
                        id=None, 
                        username=created_user.username, 
                        name=created_user.name,
                        email=created_user.email, 
                        gender=created_user.gender, 
                        role=role,
                        password_hash=password_hash, 
                        department=profile_data['department'],
                        user_id_fk=created_user.id
                    )
                    return self.instructor_repo.create(instructor)

            except Exception as profile_err:
                # ROLLBACK: Remove User if Profile creation fails
                self.user_repo.delete(created_user.id)
                raise profile_err

        except Exception as e:
            self.handle_db_error(e)