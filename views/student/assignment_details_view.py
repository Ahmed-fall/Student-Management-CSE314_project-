import tkinter as tk
from tkinter import ttk, messagebox
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from datetime import datetime
from ui.components.sidebar import Sidebar

class AssignmentDetailsView(BaseView):
    def __init__(self, parent, router, *args, **kwargs):
        # --- FIX: Extract assignment_id correctly from context ---
        self.assignment_id = kwargs.get("assignment_id")
        
        super().__init__(parent, router, *args, **kwargs)

    def create_controller(self):
        from controllers.student_controller import StudentController
        return StudentController(self.router)

    def setup_ui(self):
        # 1. Main Layout (With Sidebar)
        main_layout = tk.Frame(self, bg=COLORS["background"])
        main_layout.pack(fill="both", expand=True)

        # Add Sidebar
        Sidebar(main_layout, self.controller).pack(side="left", fill="y")

        # Content Area
        self.container = tk.Frame(main_layout, bg=COLORS["background"], padx=40, pady=30)
        self.container.pack(side="right", fill="both", expand=True)

        # 2. Header & Back Button
        header = tk.Frame(self.container, bg=COLORS["background"])
        header.pack(fill="x", pady=(0, 20))

        tk.Button(header, text="← Back to List", 
                  font=FONTS["small"], bg=COLORS["background"], fg="gray", bd=0, cursor="hand2",
                  command=self._go_back).pack(anchor="w")

        # 3. Content Details
        self.title_lbl = tk.Label(self.container, text="Loading Assignment...", font=FONTS["h1"], 
                                  bg=COLORS["background"], fg=COLORS["primary"], wraplength=800, justify="left")
        self.title_lbl.pack(anchor="w", pady=(10, 5))

        self.meta_lbl = tk.Label(self.container, text="", font=FONTS["small_bold"], 
                                 bg=COLORS["background"], fg="gray")
        self.meta_lbl.pack(anchor="w", pady=(0, 20))

        # Description Box
        tk.Label(self.container, text="Instructions:", font=FONTS["h2"], bg=COLORS["background"]).pack(anchor="w")
        
        self.desc_text = tk.Text(self.container, height=6, font=FONTS["body"], 
                                 bg="#f8f9fa", relief="flat", padx=10, pady=10)
        self.desc_text.pack(fill="x", pady=(5, 20))
        self.desc_text.config(state="disabled") # Read-only

        # 4. Submission Area
        tk.Label(self.container, text="Your Work:", font=FONTS["h2"], bg=COLORS["background"]).pack(anchor="w")
        
        self.submission_entry = tk.Text(self.container, height=8, font=FONTS["body"], 
                                        bg="white", relief="solid", bd=1, padx=10, pady=10)
        self.submission_entry.pack(fill="x", pady=(5, 10))

        # Buttons
        btn_frame = tk.Frame(self.container, bg=COLORS["background"])
        btn_frame.pack(fill="x", pady=10)

        self.submit_btn = tk.Button(btn_frame, text="Turn In", font=FONTS["body_bold"], 
                                    bg=COLORS["accent"], fg="white", padx=20, pady=10, cursor="hand2",
                                    command=self.submit_work)
        self.submit_btn.pack(side="right")

        # 5. Logic Check
        if self.assignment_id:
            # We call the controller to fetch data
            self.controller.load_assignment_details(self.assignment_id, self.update_ui)
        else:
            messagebox.showerror("Error", "No assignment ID found.")
            self._go_back()

    def update_ui(self, data):
        if not data:
            messagebox.showerror("Error", "Could not load assignment details.")
            self._go_back()
            return

        assignment = data["assignment"]
        submission = data["submission"]
        grade = data["grade"]

        self.title_lbl.config(text=assignment.title)
        meta_text = f"Due: {assignment.due_date}  |  Points: {assignment.max_score}"
        
        # Enable text widget to insert description, then disable again
        self.desc_text.config(state="normal")
        self.desc_text.delete("1.0", tk.END)
        self.desc_text.insert("1.0", assignment.description or "No instructions provided.")
        self.desc_text.config(state="disabled")

        now = datetime.now()
        due_dt = datetime.fromisoformat(assignment.due_date)
        is_overdue = now > due_dt

        if grade:
            meta_text += f"  |  Grade: {grade.grade_value} / {assignment.max_score}  |  Feedback: {grade.feedback}"
            self.meta_lbl.config(text=meta_text)
            self.submission_entry.insert("1.0", submission.content)
            self.submission_entry.config(state="disabled")
            self.submit_btn.config(text="Graded", state="disabled")
        elif submission:
            self.meta_lbl.config(text=meta_text + "  |  Status: Submitted")
            self.submission_entry.insert("1.0", submission.content)
            if is_overdue:
                self.submission_entry.config(state="disabled")
                self.submit_btn.config(text="Overdue", state="disabled")
            else:
                self.submit_btn.config(text="Update Submission")
        else:
            if is_overdue:
                self.meta_lbl.config(text=meta_text + "  |  Status: Overdue")
                self.submission_entry.config(state="disabled")
                self.submit_btn.config(text="Overdue", state="disabled")
            else:
                self.meta_lbl.config(text=meta_text + "  |  Status: Pending")

    def submit_work(self):
        content = self.submission_entry.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Validation", "You cannot submit empty work.")
            return
        
        if messagebox.askyesno("Confirm", "Are you ready to turn this in?"):
            self.controller.submit_assignment(self.assignment_id, content, self.on_submit_complete)

    def on_submit_complete(self, result):
        if result:
            messagebox.showinfo("Success", "Assignment submitted successfully!")
            self.router.navigate("student_grades")
        else:
            messagebox.showerror("Error", "Submission failed. Please try again.")

    def _go_back(self):
        self.router.navigate("student_assignments")