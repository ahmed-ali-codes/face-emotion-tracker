import threading

class AppState:
    def __init__(self):
        self._lock = threading.Lock()
        
        # Available filters
        self.FILTERS = ["Normal", "Black & White", "Thermal", "Background Blur"]
        self._current_filter_index = 0
        
        self.security_mode = False
        self.running = True
        self.current_emotion = "Neutral"

    @property
    def current_filter(self):
        with self._lock:
            return self.FILTERS[self._current_filter_index]

    def next_filter(self):
        with self._lock:
            self._current_filter_index = (self._current_filter_index + 1) % len(self.FILTERS)
            print(f"Filter changed to: {self.FILTERS[self._current_filter_index]}")

    def prev_filter(self):
        with self._lock:
            self._current_filter_index = (self._current_filter_index - 1) % len(self.FILTERS)
            print(f"Filter changed to: {self.FILTERS[self._current_filter_index]}")

    def toggle_security_mode(self):
        with self._lock:
            self.security_mode = not self.security_mode
            print(f"Security Mode: {'ON' if self.security_mode else 'OFF'}")

    def set_running(self, state: bool):
        with self._lock:
            self.running = state

    def is_running(self) -> bool:
        with self._lock:
            return self.running

    def update_emotion(self, emotion: str):
        with self._lock:
            self.current_emotion = emotion

# Global singleton instance
app_state = AppState()
