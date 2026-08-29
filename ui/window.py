import tkinter as tk
from PIL import Image, ImageTk
from core.app_state import app_state

class SmartCameraWindow:
    def __init__(self, camera, face_tracker, gesture_tracker, background_segmenter):
        self.camera = camera
        self.face_tracker = face_tracker
        self.gesture_tracker = gesture_tracker
        self.background_segmenter = background_segmenter

        self.window = tk.Tk()
        self.window.title("Advanced Smart Camera")
        self.window.geometry("1000x800")
        self.window.configure(bg="#222222")
        self.window.minsize(800, 600)

        # Control Panel
        self.control_frame = tk.Frame(self.window, bg="#333333", height=80)
        self.control_frame.pack(side=tk.TOP, fill=tk.X)

        self.sec_btn = tk.Button(
            self.control_frame, 
            text="Toggle Security Mode", 
            command=self._toggle_security,
            bg="#555555", fg="black", font=("Arial", 12, "bold")
        )
        self.sec_btn.pack(side=tk.LEFT, padx=20, pady=20)

        self.filter_lbl = tk.Label(
            self.control_frame, 
            text="Filter: Normal",
            bg="#333333", fg="white", font=("Arial", 14, "bold")
        )
        self.filter_lbl.pack(side=tk.RIGHT, padx=20, pady=20)

        # Video Label
        self.video_label = tk.Label(self.window, bg="black")
        self.video_label.pack(fill=tk.BOTH, expand=True)

        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Keep on top briefly for macOS
        try:
            self.window.call("wm", "attributes", ".", "-topmost", "1")
            self.window.after_idle(self.window.call, "wm", "attributes", ".", "-topmost", "0")
        except Exception:
            pass

        self._update_loop()

    def _toggle_security(self):
        app_state.toggle_security_mode()
        if app_state.security_mode:
            self.sec_btn.configure(text="Security: ON", bg="red")
        else:
            self.sec_btn.configure(text="Toggle Security Mode", bg="#555555")

    def _update_loop(self):
        if not app_state.is_running():
            return

        frame = self.camera.get_frame()
        if frame is not None:
            # 1. Background Segmentation (Filter)
            frame = self.background_segmenter.apply_filter(frame)
            
            # 2. Gesture Tracking
            frame = self.gesture_tracker.process_frame(frame)
            
            # 3. Face Tracking & Emotion
            frame = self.face_tracker.process_frame(frame)

            # Update UI labels
            self.filter_lbl.configure(text=f"Filter: {app_state.current_filter}")

            # Convert for Tkinter
            rgb_frame = frame # It's in BGR right now, but mediapipe might change it? Wait, frame is BGR.
            # cvtColor needed for PIL
            import cv2
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)

            # Resize to fit label
            label_width = max(self.video_label.winfo_width(), 1)
            label_height = max(self.video_label.winfo_height(), 1)
            
            img_ratio = img.width / img.height
            label_ratio = label_width / label_height
            
            if label_ratio > img_ratio:
                new_height = label_height
                new_width = int(img_ratio * new_height)
            else:
                new_width = label_width
                new_height = int(new_width / img_ratio)

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            imgtk = ImageTk.PhotoImage(img)

            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.window.after(15, self._update_loop)

    def on_close(self):
        print("🔴 Closing application...")
        app_state.set_running(False)
        self.camera.release()
        self.window.destroy()

    def start(self):
        self.window.mainloop()
