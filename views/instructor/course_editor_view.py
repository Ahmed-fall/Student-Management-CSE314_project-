# views/instructor/course_editor_view.py
import tkinter as tk
from core.base_view import BaseView

class CourseEditorView(BaseView):
    """
    [DEPRECATED] 
    Functionality moved to InstructorGradingView.
    """
    def create_controller(self):
        return None

    def setup_ui(self):
        tk.Label(self, text="This view has been removed.", font=("Helvetica", 16)).pack(pady=50)