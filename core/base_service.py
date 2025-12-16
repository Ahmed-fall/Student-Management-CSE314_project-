class BaseService:
    """
    Abstract Base Class for Services.
    """

    def check_permission(self, owner_id: int, user_id: int):
        """
        Simple logic check: Is the user acting on their own data?
        
        Args:
            owner_id: The ID found in the database (e.g., course.instructor_id)
            user_id: The ID of the person currently logged in.
        """
        if owner_id != user_id:
            raise PermissionError("Access Denied: You do not own this resource.")

    def handle_db_error(self, error: Exception):
        """
        Standardizes error messages so the UI doesn't crash with raw SQL errors.
        """
        # You can add print(error) here for debugging if needed
        raise Exception(f"System Error: {str(error)}")