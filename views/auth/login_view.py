import tkinter as tk
from tkinter import ttk
from core.base_view import BaseView
from ui.styles import COLORS, FONTS, LAYOUT

class LoginView(BaseView):
    def create_controller(self):
        from controllers.auth_controller import AuthController
        return AuthController(self.router)

    def setup_ui(self):
        # 1. Main Background
        self.configure(bg=COLORS["background"])

        # 2. The Centered Card
        # Added highlightthickness/background for a subtle border effect
        self.card = tk.Frame(self, bg=COLORS["surface"], 
                             padx=40, pady=40,
                             highlightthickness=1, highlightbackground="#e0e0e0")
        
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=400)

        # --- Header Section ---
        # Logo / Icon
        tk.Label(self.card, text="🎓", font=("Segoe UI Emoji", 48), 
                 bg=COLORS["surface"]).pack(pady=(0, 10))

        # Title
        tk.Label(self.card, text="Student System", font=FONTS["h1"], 
                 bg=COLORS["surface"], fg=COLORS["primary"]).pack(pady=(0, 5))
        
        tk.Label(self.card, text="Sign in to continue", 
                 font=FONTS["body"], bg=COLORS["surface"], fg="gray").pack(pady=(0, 20))

        # --- Error Label (Hidden by default) ---
        self.error_label = tk.Label(self.card, text="", font=FONTS["small"], 
                                    bg=COLORS["surface"], fg=COLORS["danger"], wraplength=300)
        self.error_label.pack(pady=(0, 10))

        # --- Inputs ---
        self.create_label("Username or Email")
        self.username_var = tk.StringVar()
        self.user_entry = self.create_entry(self.username_var)
        self.user_entry.focus() # Auto-focus

        self.create_label("Password")
        self.password_var = tk.StringVar()
        
        # Password Container (for the eye icon)
        pass_frame = tk.Frame(self.card, bg=COLORS["surface"])
        pass_frame.pack(fill="x", pady=5)
        
        self.pass_entry = ttk.Entry(pass_frame, textvariable=self.password_var, show="*")
        self.pass_entry.pack(side="left", fill="x", expand=True, ipady=3)
        
        # Eye Icon
        self.show_pass_var = tk.BooleanVar(value=False)
        self.eye_btn = tk.Button(pass_frame, text="👁", font=FONTS["icon"],
                                 bg=COLORS["surface"], bd=0, cursor="hand2",
                                 activebackground=COLORS["surface"], fg="gray",
                                 command=self.toggle_password)
        self.eye_btn.pack(side="right", padx=5)

        # --- Key Bindings ---
        self.user_entry.bind('<Return>', lambda e: self.pass_entry.focus())
        self.pass_entry.bind('<Return>', lambda e: self.handle_login())

        # --- Buttons ---
        # Login Button
        self.login_btn = ttk.Button(self.card, text="Sign In", style="Primary.TButton", 
                                    command=self.handle_login)
        self.login_btn.pack(fill="x", pady=(30, 15), ipady=5)

        # Divider
        tk.Frame(self.card, bg="#eee", height=1).pack(fill="x", pady=10)

        # Register Link
        tk.Label(self.card, text="Don't have an account?", 
                 font=FONTS["small"], bg=COLORS["surface"], fg="gray").pack()
        
        reg_btn = tk.Button(self.card, text="Create Account", 
                            font=FONTS["body_bold"], bg=COLORS["surface"], 
                            fg=COLORS["secondary"], bd=0, cursor="hand2",
                            activebackground=COLORS["surface"],
                            command=lambda: self.controller.go_to_register())
        reg_btn.pack(pady=(5,0))

    # --- Helpers ---

    def create_label(self, text):
        tk.Label(self.card, text=text, font=FONTS["body_bold"], 
                 bg=COLORS["surface"], fg=COLORS["text"], anchor="w").pack(fill="x", pady=(10, 5))

    def create_entry(self, variable):
        entry = ttk.Entry(self.card, textvariable=variable)
        entry.pack(fill="x", ipady=3)
        return entry

    def toggle_password(self):
        if self.show_pass_var.get():
            self.pass_entry.config(show="*")
            self.eye_btn.config(fg="gray")
            self.show_pass_var.set(False)
        else:
            self.pass_entry.config(show="")
            self.eye_btn.config(fg=COLORS["primary"])
            self.show_pass_var.set(True)

    def show_error(self, message):
        """Updates the error label text."""
        self.error_label.config(text=message)

    def handle_login(self):
        """Validates input before calling controller."""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        # 1. View-level Validation
        if not username or not password:
            self.show_error("⚠️ Please enter both username and password.")
            return

        # 2. Reset Error
        self.show_error("")
        
        # 3. Call Controller (Pass the callback for error handling)
        self.controller.login(username, password, on_fail=self.show_error)