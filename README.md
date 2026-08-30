# Advanced Smart Camera: Face & Emotion Tracker

An intelligent real-time computer vision application that tracks faces, analyzes emotions, responds to hand gestures, and acts as a smart security monitor.

## Features

- **Real-Time Face Tracking**: Uses OpenCV and `face_recognition` to detect and track known/unknown faces in real-time.
- **Emotion Analysis**: Deep learning-based emotion analysis via `deepface` to detect 7 distinct moods (Happy, Sad, Angry, Surprise, Fear, Disgust, Neutral).
- **Hand Gesture Tracking**: Powered by the modern `MediaPipe Tasks API`.
  - **Swipe Left/Right** with your index finger to cycle through camera filters.
  - Hold up a **Peace Sign** to automatically capture a screenshot.
- **Dynamic Visual Filters**: Applies filters behind the UI using `MediaPipe ImageSegmenter`.
  - Normal
  - Background Blur (Virtual Green Screen)
  - Thermal Vision
  - Black & White
- **Security & Alerting**: Triggers automated security alerts when unknown faces are detected.
- **Apple Silicon Compatible**: Fully updated to run on macOS ARM64 with Python 3.13 by leveraging the newest MediaPipe Task APIs.

## Architecture

- `core/`: Core application state and camera handling.
- `ai_modules/`: AI logic including face tracking, emotion analysis, gesture recognition, and background segmentation.
- `integrations/`: Integrations with external services like security alerting.
- `ui/`: User interface and window management built with Tkinter.

## Setup

1. Install dependencies (Requires Python 3.10+):
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Set up your `.env` file based on `.env.example`.
3. Add reference images of known faces to the `reference_faces/` directory. The filename will be used as the person's name (e.g., `Ahmed.png`).
4. Run the application:
   ```bash
   python main.py
   ```
