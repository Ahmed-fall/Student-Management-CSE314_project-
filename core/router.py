import tkinter as tk

class Router:
    def __init__(self, root_window):
        self.root = root_window
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)
        self.routes = {}
        
      
        self.history = []

    def register(self, name, view_class):
        """Teaches the router about a new page."""
        self.routes[name] = view_class

    def navigate(self, route_name, *args, **kwargs):
        """Switches the current screen to the new route and saves history."""
        if route_name not in self.routes:
            raise ValueError(f"Route '{route_name}' not registered.")

        # 1. Add the destination to the history stack
        self.history.append((route_name, args, kwargs))

        # 2. Render the view
        self._render_view(route_name, *args, **kwargs)

    def go_back(self):
        """
        Removes the current page from history and renders the previous one.
        Connected to the 'Cancel' or 'Back' buttons.
        """
        if len(self.history) > 1:
            # 1. Remove current page from the stack
            self.history.pop()
            
            # 2. Look at the previous page (the new top of the stack)
            previous_route, args, kwargs = self.history[-1]
            
            # 3. Render it (without adding to history again)
            self._render_view(previous_route, *args, **kwargs)
        else:
            print("Router: No history to go back to (already at root).")

    def _render_view(self, route_name, *args, **kwargs):
        """Internal helper to wipe the screen and draw the new one."""
        # 1. Clear old screen
        for widget in self.container.winfo_children():
            widget.destroy()

        # 2. Build new screen
        view_class = self.routes[route_name]
        
        # We pass 'self' (the router) so the new view can navigate further
        new_view = view_class(self.container, self, *args, **kwargs)
        new_view.pack(fill="both", expand=True)