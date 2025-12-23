import tkinter as tk
from tkinter import ttk, messagebox
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar

class InstructorDashboardView(BaseView):
    """
    Primary landing page for Instructors.
    Displays profile information and a list of taught courses.
    """

    def create_controller(self):
        """Links the view to the specialized Instructor logic."""
        from controllers.instructor_controller import InstructorController
        return InstructorController(self.router)

    def setup_ui(self):
        """Initializes the UI layout and triggers the data fetch."""
        # 1. Main Layout Container
        self.main_layout = tk.Frame(self, bg=COLORS["background"])
        self.main_layout.pack(fill="both", expand=True)

        # 2. Sidebar (Faculty Version)
        # Note: You can customize the Sidebar class to show different buttons for Instructors
        self.sidebar = Sidebar(self.main_layout, self.controller)
        self.sidebar.pack(side="left", fill="y")

        # 3. Content Area
        self.content = tk.Frame(self.main_layout, bg=COLORS["background"], padx=30, pady=30)
        self.content.pack(side="right", fill="both", expand=True)

        # Welcome Header
        self.welcome_lbl = tk.Label(
            self.content, 
            text="Instructor Dashboard", 
            font=FONTS["h1"], 
            bg=COLORS["background"], 
            fg=COLORS["primary"]
        )
        self.welcome_lbl.pack(anchor="w", pady=(0, 20))

        # 4. Courses Section
        tk.Label(
            self.content, 
            text="My Taught Courses", 
            font=FONTS["h2"], 
            bg=COLORS["background"]
        ).pack(anchor="w", pady=(20, 10))

        # Container for the dynamic list of courses
        self.course_list_container = tk.Frame(self.content, bg=COLORS["background"])
        self.course_list_container.pack(fill="both", expand=True)

        # 5. Load Data
        # Calls the controller which uses InstructorService
        self.controller.load_dashboard_data(self.render_dashboard)

        
    def render_dashboard(self, data):
        """Callback to populate the UI once the controller fetches the data."""
        profile = data.get("profile")
        courses = data.get("courses", [])
                
        if profile:
            self.welcome_lbl.config(text=f"Welcome, Prof. {profile.name}")

        for widget in self.course_list_container.winfo_children():
            widget.destroy()

        if not courses:
            tk.Label(self.course_list_container, text="No courses assigned yet.", 
                     font=FONTS["body"], bg=COLORS["background"]).pack(pady=20)
            return

        # Use a scrollable container if there are many courses
        for course in courses:
            self._create_course_card(course)

    def _create_course_card(self, course):
        """Creates a stylized card with management, student view, and drop options."""
        card = tk.Frame(self.course_list_container, bg="white", padx=20, pady=15, highlightthickness=1, highlightbackground="#E0E0E0")
        card.pack(fill="x", pady=8)

        # Left: Course Information
        info = tk.Frame(card, bg="white")
        info.pack(side="left")

        tk.Label(info, text=f"{course.code}: {course.name}", font=FONTS["body_bold"], bg="white").pack(anchor="w")
        tk.Label(info, text=f"Semester: {course.semester}", font=FONTS["small"], bg="white", fg="gray").pack(anchor="w")

        # Right: Action Buttons Frame
        btn_frame = tk.Frame(card, bg="white")
        btn_frame.pack(side="right")

        # 1. Manage Assignments (Passes ID to Controller for Context)
        tk.Button(btn_frame, text="Manage", bg=COLORS["secondary"], fg="white", font=FONTS["button"], padx=15,
                        command=lambda: self.router.navigate("instructor_grading", course_id=course.id)).pack(side="left", padx=5)

        # 2. View Enrolled Students
        tk.Button(btn_frame, text="👥 Students", bg="white", font=FONTS["small_bold"],
                  command=lambda: self.show_students_popup(course.id)).pack(side="left", padx=5)

        # 3. Drop Course (Unassign)
        tk.Button(btn_frame, text="❌ Drop", bg="#FFEBEE", fg="red", font=FONTS["small_bold"],
                  command=lambda: self.confirm_drop(course.id)).pack(side="left", padx=5)

    def show_students_popup(self, course_id):
        """Triggers the controller to fetch and show student details."""
        self.controller.get_course_students(course_id, self.render_students_list)

    def confirm_drop(self, course_id):
            """Confirms and then calls the drop logic via controller."""
            if messagebox.askyesno("Unassign Course", "Are you sure you want to stop teaching this course?"):
                # FIX: We reload data and call 'render_dashboard' to refresh ONLY the list.
                # We do NOT call 'setup_ui' because that draws a whole new screen on top.
                self.controller.drop_teaching_course(
                    course_id, 
                    lambda result: self.controller.load_dashboard_data(self.render_dashboard) if result else None
                )

    def refresh_view(self):
        """Clears the entire screen and rebuilds the UI."""
        # 1. Destroy all existing widgets (Sidebar, Content, etc.)
        for widget in self.winfo_children():
            widget.destroy()
        
        # 2. Re-run setup to build a fresh UI
        self.setup_ui()

    def render_students_list(self, students):
        """Creates a popup window to display enrollment details."""
        popup = tk.Toplevel(self)
        popup.title("Course Enrollment")
        popup.geometry("350x450")
        popup.configure(bg="white")

        tk.Label(popup, text=f"Enrolled Students ({len(students)})", font=FONTS["h2"], bg="white").pack(pady=15)
        
        list_frame = tk.Frame(popup, bg="white")
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        for s in students:
            # Assuming student profile has name and major
            lbl = tk.Label(list_frame, text=f"• {s.name} [{s.major}]", bg="white", font=FONTS["body"], anchor="w")
            lbl.pack(fill="x", pady=2)