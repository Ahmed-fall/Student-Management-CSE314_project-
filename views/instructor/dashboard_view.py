import tkinter as tk
from core.base_view import BaseView
from ui.styles import FONTS, COLORS

class InstructorDashboardView(BaseView):
    def create_controller(self):
        return None # Placeholder

    def setup_ui(self):
        tk.Label(self, text="Instructor Dashboard", font=FONTS["h1"], fg=COLORS["primary"]).pack(pady=50)
        tk.Label(self, text="Manage your courses here.", font=FONTS["body"]).pack()
        
        tk.Button(self, text="Logout", command=lambda: self.router.navigate("login")).pack(pady=20)