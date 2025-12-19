# core/base_controller.py
from tkinter import messagebox
from core.service_locator import ServiceLocator
from core.async_task import AsyncTask

class BaseController:
    def __init__(self, router):
        self.router = router

    def get_service(self, service_class):
        """Helper to get a service from the locator."""
        return ServiceLocator.get(service_class)

    def run_async(self, task_func, success_callback):
        """
        Runs 'task_func' in background. 
        Calls 'success_callback(result)' on UI thread when done.
        """
        # We wrap the callback to ensure it runs on the main loop if needed
        # (Tkinter is sensitive about threads, but keeping it simple here)
        AsyncTask(task_func, success_callback, self.handle_exception)

    def navigate(self, route_name, *args, **kwargs):
        self.router.navigate(route_name, *args, **kwargs)

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def show_success(self, title, message):
        messagebox.showinfo(title, message)
    
    def handle_exception(self, e):
        print(f"System Error: {e}")
        self.show_error("System Error", str(e))