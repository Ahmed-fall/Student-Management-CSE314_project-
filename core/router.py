# core/router.py
import tkinter as tk

class Router:
    def __init__(self, root_window):
        self.root = root_window
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)
        self.routes = {}

    def register(self, name, view_class):
        """Teaches the router about a new page."""
        self.routes[name] = view_class

    def navigate(self, route_name, *args, **kwargs):
        """Switches the current screen to the new route."""
        if route_name not in self.routes:
            raise ValueError(f"Route '{route_name}' not registered.")

        # 1. Clear old screen
        for widget in self.container.winfo_children():
            widget.destroy()

        # 2. Build new screen
        view_class = self.routes[route_name]
        # We pass 'self' (the router) so the new view can navigate further
        new_view = view_class(self.container, self, *args, **kwargs)
        new_view.pack(fill="both", expand=True)