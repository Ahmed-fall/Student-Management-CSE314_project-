from core.base_controller import BaseController
from services.auth_service import AuthService
from core.session import Session

class AuthController(BaseController):
    
    # --- Login Logic ---
    def login(self, username, password, on_fail=None):
        
        # 1. Validation
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
                # Success: Clear any error messages first
                if on_fail: on_fail("") 

                # Update Session
                Session.login(user)
                
                # Navigate based on Role
                if user.role == "student":
                    self.navigate("student_dashboard")
                elif user.role == "instructor":
                    self.navigate("instructor_dashboard")
                elif user.role == "admin":
                    self.navigate("admin_dashboard")
                else:
                    self.show_error("Access Denied", f"Role '{user.role}' not supported yet.")
            else:
                # Failure: Update the View's error label
                error_msg = "Invalid username or password."
                if on_fail:
                    on_fail(error_msg)
                else:
                    self.show_error("Login Failed", error_msg)

        # 4. Execute
        self.run_async(db_task, on_complete)

    # --- Registration Logic ---
    def register(self, user_data, profile_data, role):
        # 1. Validation
        if not user_data.get('username') or not user_data.get('password'):
            self.show_error("Validation Error", "Username and Password are required.")
            return

        # 2. Background Task
        def db_task():
            service = self.get_service(AuthService)
            return service.register(user_data, profile_data, role)

        # 3. Completion Callback
        def on_complete(new_user):
            if new_user:
                self.show_success("Success", "Account created successfully! Please login.")
                self.navigate("login") # Go back to login screen

        # 4. Execute
        self.run_async(db_task, on_complete)

    # --- Navigation Helpers (These were missing!) ---
    def go_to_register(self):
        self.navigate("register")

    def go_to_login(self):
        self.navigate("login")