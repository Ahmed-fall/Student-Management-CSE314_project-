from core.base_service import BaseService
from repositories.user_repo import UserRepository
from models.user import User

class UserService(BaseService):
    """
    Manages core user profile data.
    Handles viewing, updating, and listing users.
    """

    def __init__(self):
        self.user_repo = UserRepository()

    def get_user_by_id(self, user_id: int):
        """
        Fetches a specific user's identity data.
        """
        try:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                raise ValueError("User not found.")
            return user
        except Exception as e:
            self.handle_db_error(e)

    def update_profile(self, user_id: int, current_user_id: int, updates: dict):
        """
        Updates non-security user information (name, email, gender).
        """
        try:
            # 1. Authorization: Ensure the user is editing their own profile
            self.check_permission(user_id, current_user_id)

            # 2. Fetch current object to apply updates
            user = self.user_repo.get_by_id(user_id)
            if not user:
                raise ValueError("User not found.")

            # 3. Apply changes to the Model (This triggers validation)
            if 'name' in updates:
                user.name = updates['name']
            if 'email' in updates:
                user.email = updates['email']
            if 'gender' in updates:
                user.gender = updates['gender']
            if 'username' in updates:
                user.username = updates['username']

            # 4. Save the validated object back to the DB
            self.user_repo.update(user)
            return user

        except Exception as e:
            self.handle_db_error(e)

    def get_all_users(self, current_user_role: str):
        """
        Lists all users. Restricted to Admin role.
        """
        try:
            # 1. Authorization: Only admins should see the full user list
            if current_user_role != "admin":
                raise PermissionError("Access Denied: Admin privileges required.")

            return self.user_repo.get_all()
        except Exception as e:
            self.handle_db_error(e)

    def delete_account(self, user_id: int, current_user_id: int):
        """
        Deletes a user account.
        """
        try:
            # Ensure user owns the account
            self.check_permission(user_id, current_user_id)
            
            self.user_repo.delete(user_id)
            return True
        except Exception as e:
            self.handle_db_error(e)