# core/base_view.py
import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod

from ui.styles import COLORS, FONTS

class BaseView(tk.Frame, ABC):
    """
    The parent class for all UI Screens (Views).
    Enforces a standard structure: __init__ -> setup_ui.
    """
    def __init__(self, parent, router, *args, **kwargs):
        super().__init__(parent)
        self.router = router
        # We allow passing data (like user_id) to views via *args
        self.view_args = args 
        
        # Every View must have a Controller
        self.controller = self.create_controller()
        
        # Build the visual elements
        self.setup_ui()

    @abstractmethod
    def create_controller(self):
        """Must return the specific Controller instance for this view."""
        pass

    @abstractmethod
    def setup_ui(self):
        """Where all the Buttons, Labels, and Entries are created."""
        pass

    def clear_content(self):
        """Helper to wipe the frame if needed."""
        for widget in self.winfo_children():
            widget.destroy()

    def add_back_button(self, parent):
        """Adds a consistent back button to the top of the page."""
        back_btn = tk.Button(
            parent, 
            text="⬅ Back", 
            command=self.router.go_back, # Uses the router's internal stack
            bg=COLORS["background"], 
            fg=COLORS["primary"],
            font=FONTS["body_bold"],
            bd=0,
            cursor="hand2"
        )
        back_btn.pack(side="left", padx=10, pady=10)