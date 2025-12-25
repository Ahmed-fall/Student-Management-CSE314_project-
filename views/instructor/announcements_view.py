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
        # --- 1. Main Layout & Background ---
        self.main_layout = tk.Frame(self, bg=COLORS["background"])
        self.main_layout.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = Sidebar(self.main_layout, self.controller)
        self.sidebar.pack(side="left", fill="y")

        # Content Area (Light Grey Background)
        self.content = tk.Frame(self.main_layout, bg=COLORS["background"])
        self.content.pack(side="right", fill="both", expand=True, padx=40, pady=40)

        # Header Section
        header_frame = tk.Frame(self.content, bg=COLORS["background"])
        # FIXED: Replaced CSS-style 'marginBottom' with Tkinter 'pady' (0 top, 20 bottom)
        header_frame.pack(fill="x", pady=(0, 20)) 
        
        tk.Label(header_frame, text="📢 Announcements", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(anchor="w")
        
        tk.Label(header_frame, text="Broadcast updates to your students instantly.", 
                 font=FONTS["caption"], bg=COLORS["background"], fg="grey").pack(anchor="w", pady=(5, 0))

        # --- 2. THE CARD (White container with shadow effect) ---
        # We simulate a card by using a white frame with generous internal padding
        self.card = tk.Frame(self.content, bg="white", padx=40, pady=40)
        self.card.pack(fill="both", expand=True)
        
        # Give the card a subtle border
        self.card.config(highlightbackground="#E0E0E0", highlightthickness=1)

        # --- FORM ELEMENTS ---

        # 1. Course Selector
        self._create_label("Select Course")
        self.course_var = tk.StringVar()
        
        # Container for the dropdown to manage spacing
        cb_frame = tk.Frame(self.card, bg="white", pady=5)
        cb_frame.pack(fill="x")
        
        self.course_cb = ttk.Combobox(cb_frame, textvariable=self.course_var, 
                                      state="readonly", font=FONTS["body"], height=5)
        self.course_cb.pack(fill="x", ipady=5) # ipady adds internal height for a modern look

        # 2. Subject Input (Modern Flat Style)
        self._create_label("Subject")
        self.subject_entry = self._create_modern_entry(self.card)

        # 3. Message Body (Modern Text Area)
        self._create_label("Message")
        self.message_body = self._create_modern_text_area(self.card, height=12)

        # 4. Action Bar (Button)
        btn_frame = tk.Frame(self.card, bg="white", pady=20)
        btn_frame.pack(fill="x")

        self.send_btn = tk.Button(btn_frame, text="🚀 Broadcast Announcement", 
                                  command=self.send_announcement_logic,
                                  bg=COLORS["secondary"], fg="white", 
                                  font=FONTS["button"], 
                                  relief="flat", cursor="hand2",
                                  padx=25, pady=12)
        self.send_btn.pack(side="right")

        # Add Hover Effect to Button
        self.send_btn.bind("<Enter>", lambda e: self.send_btn.config(bg="#3E8E41")) # Darker Green
        self.send_btn.bind("<Leave>", lambda e: self.send_btn.config(bg=COLORS["secondary"]))

        # --- LOAD DATA ---
        self.controller.load_my_courses_for_selector(self.populate_dropdown)

    # --- UI HELPERS FOR MODERN LOOK ---
    
    def _create_label(self, text):
        """Helper to create consistent bold labels."""
        tk.Label(self.card, text=text, bg="white", fg=COLORS["primary"],
                 font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(20, 8))

    def _create_modern_entry(self, parent):
        """Creates a flat entry with a colored border frame."""
        # The Frame acts as the border
        border_frame = tk.Frame(parent, bg="#CCCCCC", bd=1)
        border_frame.pack(fill="x", ipady=1) # ipady gives the border thickness

        # The Entry sits inside
        entry = tk.Entry(border_frame, font=FONTS["body"], bg="#F9F9F9", relief="flat")
        entry.pack(fill="both", padx=1, pady=1, ipady=8) # ipady=8 makes the input taller (modern)

        # Focus Effects (Highlight border on click)
        def on_focus_in(e): border_frame.config(bg=COLORS["primary"])
        def on_focus_out(e): border_frame.config(bg="#CCCCCC")
        
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        
        return entry

    def _create_modern_text_area(self, parent, height):
        """Creates a flat text area with a colored border frame."""
        border_frame = tk.Frame(parent, bg="#CCCCCC", bd=1)
        border_frame.pack(fill="x")

        text_widget = tk.Text(border_frame, height=height, font=FONTS["body"], 
                              bg="#F9F9F9", relief="flat", padx=10, pady=10)
        text_widget.pack(fill="x", padx=1, pady=1)

        def on_focus_in(e): border_frame.config(bg=COLORS["primary"])
        def on_focus_out(e): border_frame.config(bg="#CCCCCC")

        text_widget.bind("<FocusIn>", on_focus_in)
        text_widget.bind("<FocusOut>", on_focus_out)

        return text_widget

    # --- LOGIC ---

    def populate_dropdown(self, courses):
        if not courses:
            self.course_cb.set("No courses available")
            self.course_cb.config(state="disabled")
            return

        self.course_map = {f"{c.code}: {c.name}": c.id for c in courses}
        self.course_cb['values'] = list(self.course_map.keys())
        self.course_cb.current(0) 

    def send_announcement_logic(self):
        selected_text = self.course_cb.get()
        course_id = self.course_map.get(selected_text) if hasattr(self, 'course_map') else None

        if not course_id:
            messagebox.showerror("Error", "Please select a valid course.")
            return

        # Note: using .get() from our new styled entry
        title = self.subject_entry.get().strip() 
        message = self.message_body.get("1.0", tk.END).strip()

        if not title or not message:
            messagebox.showwarning("Validation", "Both subject and message are required.")
            return

        if messagebox.askyesno("Confirm", f"Send this to all students in {selected_text}?"):
            self.controller.create_announcement(course_id, title, message, self.on_announcement_success)

    def on_announcement_success(self, result):
        if result:
            messagebox.showinfo("Success", "Announcement broadcasted successfully!")
            self.subject_entry.delete(0, tk.END)
            self.message_body.delete("1.0", tk.END)