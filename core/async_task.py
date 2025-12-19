# core/async_task.py
import threading
import tkinter as tk

class AsyncTask:
    """
    Runs a heavy function in a separate thread.
    When finished, updates the UI on the main thread.
    """
    def __init__(self, target_func, callback_func, error_callback=None):
        self.target = target_func
        self.callback = callback_func
        self.error_callback = error_callback
        
        # FIX: daemon=True means "Kill this thread if the main app closes"
        self.thread = threading.Thread(target=self._run, daemon=True) 
        self.thread.start()

    def _run(self):
        try:
            result = self.target()
            # Schedule the callback on the main UI thread
            # We assume the root window is accessible or passed via closure
            self.callback(result)
        except Exception as e:
            if self.error_callback:
                self.error_callback(e)
            else:
                print(f"Async Error: {e}")