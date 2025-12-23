import tkinter as tk
from core.router import Router
from ui.styles import setup_theme, COLORS

# Import Views
from views.auth.login_view import LoginView
from views.auth.register_view import RegisterView
from views.student.dashboard_view import StudentDashboardView
from views.instructor.dashboard_view import InstructorDashboardView
from views.instructor.course_editor_view import CourseEditorView
from views.instructor.grading_view import InstructorGradingView
from views.instructor.announcements_view import InstructorAnnouncementsView
from views.instructor.campus_manager_view import CampusManagerView

# --- NEW IMPORTS (Required for Sidebar Navigation) ---
from views.student.courses_view import StudentCoursesView
from views.student.assignments_view import StudentAssignmentsView
from views.student.grades_view import StudentGradesView
from views.student.notifications_view import StudentNotificationsView
from views.student.classroom_view import ClassroomView
from views.student.assignment_details_view import AssignmentDetailsView
from views.student.catalog_view import StudentCatalogView

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        
        # 1. Define dimensions
        width = 1280
        height = 800
        
        # 2. Calculate Center Position
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # 3. Apply Geometry
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(1024, 768)
        
        setup_theme(self.root)
        
        self.router = Router(self.root)
        
        # --- Register Routes ---
        self.router.register("login", LoginView)
        self.router.register("register", RegisterView)
        self.router.register("student_dashboard", StudentDashboardView)
        self.router.register("instructor_dashboard", InstructorDashboardView)
        self.router.register("student_dashboard", StudentDashboardView)
        
        
        # --- NEW REGISTRATIONS (Connects the Sidebar Buttons) ---
        self.router.register("student_courses", StudentCoursesView)
        self.router.register("student_assignments", StudentAssignmentsView)
        self.router.register("student_grades", StudentGradesView)
        self.router.register("student_classroom", ClassroomView)
        self.router.register("student_assignment_details", AssignmentDetailsView)
        self.router.register("student_notifications", StudentNotificationsView)
        self.router.register("student_catalog", StudentCatalogView)
        
        self.router.register("instructor_dashboard", InstructorDashboardView)        
        self.router.register("course_editor", CourseEditorView) 
        self.router.register("instructor_grading", InstructorGradingView)
        self.router.register("instructor_announcements", InstructorAnnouncementsView)
        self.router.register("campus_manager", CampusManagerView)
        
        self.router.navigate("login")



    def run(self):
        self.root.mainloop()