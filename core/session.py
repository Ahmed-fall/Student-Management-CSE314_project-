# core/session.py

class Session:
    """
    A global singleton that holds the state of the active user.
    """
    current_user = None
    current_course_id = None

    @classmethod
    def login(cls, user):
        """Sets the current user after successful auth."""
        cls.current_user = user
        print(f"[Session] User logged in: {user.username} ({user.role})")

    @classmethod
    def logout(cls):
        """Clears the session."""
        print(f"[Session] User logged out: {cls.current_user.username if cls.current_user else 'None'}")
        cls.current_user = None

    @classmethod
    def is_logged_in(cls) -> bool:
        return cls.current_user is not None