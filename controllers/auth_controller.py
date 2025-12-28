from core.base_controller import BaseController
from services.auth_service import AuthService
from core.session import Session

class AuthController(BaseController):
    
    # -------------------------------------------------------------------------
    # Login Logic
    # -------------------------------------------------------------------------
    def login(self, username, password, on_fail=None):
        
        # 1. Basic Input Validation
        if not username or not password:
            error_msg = "Please enter both username and password."
            if on_fail:
                on_fail(error_msg)
            else:
                self.show_error("Validation Error", error_msg)
            return

        # 2. Define the heavy task (Runs in background)
        def db_task():
            service = self.get_service(AuthService)
            return service.login(username, password)

        # 3. Define what happens when DB finishes
        def on_complete(user):
            if user:
                # Success: Clear error messages
                if on_fail: on_fail("") 

                # Update Global Session
                Session.login(user)
                
                # Navigate based on Role
                role_map = {
                    "student": "student_dashboard",
                    "instructor": "instructor_dashboard",
                    "admin": "admin_dashboard"
                }
                
                target_view = role_map.get(user.role)
                if target_view:
                    self.navigate(target_view)
                else:
                    self.show_error("Access Denied", f"Role '{user.role}' not supported yet.")
            else:
                # Failure logic
                error_msg = "Invalid username or password."
                if on_fail:
                    on_fail(error_msg)
                else:
                    self.show_error("Login Failed", error_msg)

        # 4. Execute
        self.run_async(db_task, on_complete)

    # -------------------------------------------------------------------------
    # Registration Logic 
    # -------------------------------------------------------------------------
    def register(self, user_data, profile_data, role):
        """
        Handles user registration.
        user_data: dict {username, password, name, email, gender}
        profile_data: dict {major, year} OR {department}
        role: str
        """

        # 1. Validation & Sanitization
        if not user_data.get('username') or not user_data.get('password'):
            self.show_error("Validation Error", "Username and Password are required.")
            return
        
        # Ensure role is lowercase for the Model
        role = role.lower() 

        # Sanitization: Ensure integer fields are actually integers
        # (Fixes the string-from-UI vs int-in-Model crash)
        try:
            if role == 'student' and 'year' in profile_data:
                profile_data['year'] = int(profile_data['year'])
        except ValueError:
            self.show_error("Validation Error", "Year must be a number.")
            return

        # 2. Background Task
        def db_task():
            service = self.get_service(AuthService)
            return service.register(user_data, profile_data, role)

        # 3. Completion Callback
        def on_complete(result):
            
            
            # Assuming run_async handles exceptions, if we get here, it succeeded.
            self.show_success("Success", "Account created successfully! Please login.")
            self.navigate("login")

        # 4. Execute
        self.run_async(db_task, on_complete)

    # -------------------------------------------------------------------------
    # Navigation Helpers
    # -------------------------------------------------------------------------
    def go_to_register(self):
        self.navigate("register")

    def go_to_login(self):
        self.navigate("login")

    def logout(self):
        Session.logout()
        self.navigate("login")