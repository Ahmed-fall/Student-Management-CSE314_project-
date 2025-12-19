import tkinter as tk
from tkinter import ttk 
from ui.styles import COLORS, FONTS


class Sidebar(tk.Frame):
    def __init__(self, parent, controller):
        
        super().__init__(parent, bg=COLORS["sidebar"], width=250)
        
        self.controller = controller
        self.pack_propagate(False) # Force width to stay 250px
        
        # App Title in Sidebar
        # Note: We use standard tk.Label here because it's easier to set specific colors (bg="#2c3e50")
        tk.Label(self, text="Student\nPortal", font=("Helvetica", 20, "bold"), 
                 bg=COLORS["sidebar"], fg="white", justify="left").pack(pady=(30, 40), padx=20, anchor="w")

        # Navigation Buttons
        self.add_nav_btn("📊  Dashboard", "student_dashboard")
        self.add_nav_btn("📚  My Courses", "student_courses") 
        self.add_nav_btn("🔍  Course Catalog", "student_catalog")
        self.add_nav_btn("📝  Assignments", "student_assignments") 
        self.add_nav_btn("🎓  Grades", "student_grades") 
        self.add_nav_btn("🔔  Notifications", "student_notifications")
        
        # Spacer to push Logout to bottom (Standard tk.Frame is fine here for simple spacer)
        tk.Frame(self, bg=COLORS["sidebar"]).pack(fill="y", expand=True) # Matches sidebar color
        
        # Logout
        self.add_nav_btn("🚪  Logout", "login")

    def add_nav_btn(self, text, route):
        btn = ttk.Button(self, text=text, style="Sidebar.TButton",
                         command=lambda: self.controller.navigate(route))
        btn.pack(fill="x", pady=2, ipady=5)