import tkinter as tk
from tkinter import ttk, messagebox
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar

class InstructorAnnouncementsView(BaseView):
    def create_controller(self):
        from controllers.instructor_controller import InstructorController
        return InstructorController(self.router)

    def setup_ui(self):
        # 1. Main Layout
        self.main_layout = tk.Frame(self, bg=COLORS["background"])
        self.main_layout.pack(fill="both", expand=True)

        self.sidebar = Sidebar(self.main_layout, self.controller)
        self.sidebar.pack(side="left", fill="y")

        self.content = tk.Frame(self.main_layout, bg=COLORS["background"], padx=30, pady=30)
        self.content.pack(side="right", fill="both", expand=True)

        # Header
        tk.Label(self.content, text="📢 Post Announcement", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(pady=(0, 20), anchor="w")

        # --- FORM CONTAINER ---
        container = tk.Frame(self.content, bg="white", padx=30, pady=30)
        container.pack(fill="both", expand=True)

        # 1. Course Selector (The Fix for 'Which Course?')
        tk.Label(container, text="Select Course:", bg="white", font=FONTS["body_bold"]).pack(anchor="w", pady=(0, 5))
        
        self.course_var = tk.StringVar()
        self.course_cb = ttk.Combobox(container, textvariable=self.course_var, state="readonly", width=40)
        self.course_cb.pack(anchor="w", pady=(0, 20))

        # 2. Subject
        tk.Label(container, text="Subject:", bg="white", font=FONTS["body_bold"]).pack(anchor="w", pady=(0, 5))
        self.subject = tk.Entry(container, font=FONTS["body"], bg="#F9F9F9")
        self.subject.pack(fill="x", pady=(0, 20), ipady=5)

        # 3. Message Body
        tk.Label(container, text="Message:", bg="white", font=FONTS["body_bold"]).pack(anchor="w", pady=(0, 5))
        self.message_body = tk.Text(container, height=10, font=FONTS["body"], bg="#F9F9F9", relief="flat", padx=10, pady=10)
        self.message_body.pack(fill="x", pady=(0, 20))

        # 4. Send Button
        tk.Button(container, text="🚀 Broadcast to Students", 
                  command=self.send_announcement_logic,
                  bg=COLORS["secondary"], fg="white", font=FONTS["button"], 
                  padx=20, pady=10).pack(anchor="e")

        # --- LOAD COURSES ---
        # Fetch courses immediately to populate the dropdown
        self.controller.load_my_courses_for_selector(self.populate_dropdown)

    def populate_dropdown(self, courses):
        """Fills the dropdown with 'CS101: Intro to CS' format."""
        if not courses:
            self.course_cb.set("No courses available")
            self.course_cb.config(state="disabled")
            return

        # Create a mapping: "Code: Name" -> ID
        self.course_map = {f"{c.code}: {c.name}": c.id for c in courses}
        
        self.course_cb['values'] = list(self.course_map.keys())
        self.course_cb.current(0) # Select first one by default

    def send_announcement_logic(self):
        """Validates input and sends to controller."""
        # 1. Get Course ID
        selected_text = self.course_cb.get()
        course_id = self.course_map.get(selected_text) if hasattr(self, 'course_map') else None

        if not course_id:
            messagebox.showerror("Error", "Please select a valid course.")
            return

        # 2. Get Text
        title = self.subject.get().strip()
        message = self.message_body.get("1.0", tk.END).strip()

        if not title or not message:
            messagebox.showwarning("Validation", "Both subject and message are required.")
            return

        # 3. Send
        if messagebox.askyesno("Confirm", f"Send this to all students in {selected_text}?"):
            self.controller.create_announcement(course_id, title, message, self.on_announcement_success)

    def on_announcement_success(self, result):
        if result:
            messagebox.showinfo("Success", "Announcement broadcasted successfully!")
            # Clear form
            self.subject.delete(0, tk.END)
            self.message_body.delete("1.0", tk.END)