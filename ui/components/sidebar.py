import tkinter as tk
from tkinter import ttk 
from ui.styles import COLORS, FONTS
from core.session import Session


# sidebar.py
class Sidebar(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["sidebar"], width=250)
        self.controller = controller
        self.pack_propagate(False)
        
        user = Session.current_user #
        role_title = "Student\nPortal" if user.role == "student" else "Faculty\nPortal"
        
        tk.Label(self, text=role_title, font=("Helvetica", 20, "bold"), 
                 bg=COLORS["sidebar"], fg="white", justify="left").pack(pady=(30, 40), padx=20, anchor="w")

        # --- DYNAMIC NAVIGATION ---
        if user.role == "student":
            self.add_nav_btn("📊  Dashboard", "student_dashboard")
            self.add_nav_btn("📚  My Courses", "student_courses") 
            self.add_nav_btn("🔍  Course Catalog", "student_catalog")
            self.add_nav_btn("📝  Assignments", "student_assignments") 
            self.add_nav_btn("🎓  Grades", "student_grades") 
            self.add_nav_btn("🔔  Notifications", "student_notifications")
        

        elif user.role == "instructor":
            self.add_nav_btn("📊  Dashboard", "instructor_dashboard")          
            self.add_nav_btn("📢  Announcements", "instructor_announcements")
            self.add_nav_btn("🏫  Campus Manager", "campus_manager")

        # Spacer and Logout
        tk.Frame(self, bg=COLORS["sidebar"]).pack(fill="y", expand=True)
        self.add_nav_btn("🚪  Logout", "login")

    def add_nav_btn(self, text, route):
        btn = ttk.Button(self, text=text, style="Sidebar.TButton",
                         command=lambda: self.controller.navigate(route))
        btn.pack(fill="x", pady=2, ipady=5)