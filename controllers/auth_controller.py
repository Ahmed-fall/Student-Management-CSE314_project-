from core.base_controller import BaseController
from services.auth_service import AuthService
from core.session import Session

class AuthController(BaseController):
    
    # --- Login Logic ---
    def login(self, username, password):
        # 1. Validation (Fast check on main thread)
        if not username or not password:
            self.show_error("Validation Error", "Please enter both username and password.")
            return

        # 2. Define the heavy task (Runs in background)
        def db_task():
            # Use get_service() instead of creating a new instance
            service = self.get_service(AuthService)
            return service.login(username, password)

        # 3. Define what happens when DB finishes
        def on_complete(user):
            if user:
                # Update Session
                Session.login(user)
                
                # Navigate based on Role
                if user.role == "student":
                    self.navigate("student_dashboard")
                elif user.role == "instructor":
                    self.navigate("instructor_dashboard")
                else:
                    self.show_error("Access Denied", f"Role '{user.role}' not supported yet.")
            else:
                self.show_error("Login Failed", "Invalid username or password.")

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