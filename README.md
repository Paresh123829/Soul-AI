Soul AI - Emotional Wellness Companion
Soul AI is a cutting-edge web-based application designed to support youth mental wellness by addressing emotional challenges like stress and anxiety through generative AI. Leveraging real-time facial emotion recognition, AI-driven chatbot interactions, and mood tracking, it offers a personalized, stigma-free platform for students to manage their emotional health. Deployable on Google Cloud Platform (GCP) with Cloud Firestore, this project integrates advanced technologies to foster resilience and well-being.
Features

Mood Detection: Uses DeepFace and webcam input to analyze facial expressions (e.g., happy, sad, angry) in real-time.
AI Chatbot: Powered by Google Gemini AI, supports text and voice interactions with tailored responses (e.g., motivational quotes, music suggestions).
Mood Logging: Tracks and displays mood history for self-awareness and pattern recognition.
Registration System: Collects user data (health, lifestyle, preferences) for a personalized experience.
Voice Input & Audio Alerts: Enables voice-based chats and triggers alerts (e.g., for negative moods) using PyDub/SimpleAudio.
Responsive UI: Built with HTML, CSS, and JavaScript for seamless use across devices.

Benefits for Students

Stress Management: Real-time mood detection with suggestions like breathing exercises or breaks.
Mental Health Support: A safe chatbot space for emotional expression and coping strategies.
Time Management: Mood history helps identify emotional patterns for better self-care.
Accessibility: User-friendly design with voice input for easy engagement.

Tech Stack

Frontend: HTML, CSS (styles.css), JavaScript (script.js) for UI and interactivity.
Backend: Flask (app.py) with Python, deployed on GCP App Engine.
AI & ML: DeepFace (emotion analysis), Google Gemini API (conversational AI).
Audio: gTTS (text-to-speech), SpeechRecognition (voice-to-text), PyDub, SimpleAudio (alerts).
Database: Cloud Firestore (NoSQL) on GCP for mood logs and user data.
Deployment: GCP App Engine, Cloud Storage (static files), Vertex AI (Gemini integration).
Dependencies: Managed via requirements.txt (e.g., flask, opencv-python, deepface, google-generativeai).

Installation
Prerequisites

Python 3.8+
Node.js (for frontend build, optional)
GCP account with billing enabled
Webcam and microphone access
Git

Steps

Clone the Repository:
git clone https://github.com/your-username/soul-ai.git
cd soul-ai


Set Up Virtual Environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:
pip install -r requirements.txt


Configure GCP:

Create a GCP project and enable billing.

Set up Cloud Firestore (select Native mode) and Cloud Storage.

Enable APIs: App Engine, Cloud Speech-to-Text, Cloud Text-to-Speech, Vertex AI.

Generate a service account key and set environment variables:
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
export GEMINI_API_KEY=your-gemini-api-key


Deploy to App Engine:
gcloud init
gcloud app deploy app.yaml --quiet


Upload static files (HTML, CSS, JS) to Cloud Storage bucket.



Run Locally (Optional):
python app.py

Access at http://localhost:5000.


Usage

Registration:

Visit the deployed URL (e.g., https://your-project-id.appspot.com) or local http://localhost:5000.
Open welcome.html, fill out the form with personal details (e.g., name, date of birth), health status, lifestyle preferences, communication style, and login credentials, then click "Complete Registration" to proceed.


Dashboard Interface:

After clicking on "Complete Registration" it navigates automatically to dashboard.html.
Mood Detector: Click "Start Detection" to activate webcam-based mood analysis; the "Current Mood" updates in real-time, with suggestions displayed below. Click "Stop Detection" to pause.
AI Assistant: Type a message in the chat input box or use the microphone icon for voice input (hold to record, releases after 3 seconds). Send via "Enter" or the send button; bot responses appear in the chat window, with a "Play Audio" button if audio is available.
Mood History: Click "View History" to display a table of past moods and times; click "Hide History" to collapse it.


Interaction Tips:

Ensure webcam/microphone permissions are granted.
Select preferred support styles (e.g., motivational quotes) during registration for tailored chatbot responses.
Check mood logs regularly to track emotional trends.



Architecture

Core: Digital Psychological Intervention System (Flask backend).
Input: Frontend (HTML/CSS/JS) captures webcam, text, voice.
Processing: Emotion Analysis (DeepFace/OpenCV), Conversational AI (Gemini API).
Storage: Data Handling (Cloud Firestore).
Output: Responses (text/audio) via gTTS, alerts via PyDub/SimpleAudio.

Limitations

Mood detection accuracy varies with lighting/camera quality.
Voice recognition depends on microphone and noise levels.
Scales with usage; optimize for high traffic.

Contact
For issues, open a GitHub issue or email pareshsm2580@gmail.com.