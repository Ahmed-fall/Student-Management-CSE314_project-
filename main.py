import tkinter as tk
from database.initialize_db import create_tables
from ui.main_window import MainWindow
from ui.styles import setup_theme

# Import Services and Locator
from core.service_locator import ServiceLocator
from services.auth_service import AuthService
from services.course_service import CourseService
from services.notification_service import NotificationService
from services.student_service import StudentService
from services.assignment_service import AssignmentService
from services.announcement_service import AnnouncementService
# ... import other services

def bootstrap_services():
    """Register all services once at startup."""
    print("--- Bootstrapping Services ---")
    ServiceLocator.register(AuthService, AuthService())
    ServiceLocator.register(CourseService, CourseService())
    ServiceLocator.register(NotificationService, NotificationService())
    ServiceLocator.register(StudentService, StudentService())
    ServiceLocator.register(AssignmentService, AssignmentService())
    ServiceLocator.register(AnnouncementService, AnnouncementService())
    # ... register others

def main():
    print("--- Starting Student Management System  ---")
    
    # 1. Infrastructure
    create_tables()
    bootstrap_services() 
    
    # 2. UI Init
    root = tk.Tk()
    setup_theme(root) 
    
    # 3. Launch
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()