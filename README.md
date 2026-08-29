# Face & Emotion Tracker

An intelligent real-time computer vision application that tracks faces, analyzes emotions, and acts as a smart security monitor.

## Features

- **Real-Time Face Tracking**: Uses OpenCV and `face_recognition` to detect and track known/unknown faces in real-time.
- **Emotion Analysis**: Deep learning-based emotion analysis via `deepface` to detect moods (e.g., Happy, Neutral, Angry).
- **Security & Alerting**: Triggers automated security alerts when unknown faces are detected.
- **Smart Home Integration**: Connects with Philips Hue to change lighting based on recognized gestures or emotions.
- **Background Segmentation & Gestures**: Tracks hand gestures and enables background removal.

## Architecture

- `core/`: Core application state and camera handling.
- `ai_modules/`: AI logic including face tracking, emotion analysis, gesture recognition, and background segmentation.
- `integrations/`: Integrations with external services like Philips Hue and security alerting.
- `ui/`: User interface and window management.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up your `.env` file based on `.env.example`.
3. Add reference images of known faces to the `reference_faces/` directory (e.g., `john.jpg`, `jane.png`).
4. Run the application:
   ```bash
   python main.py
   ```
