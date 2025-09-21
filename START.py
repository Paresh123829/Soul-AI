import cv2
from deepface import DeepFace
from plyer import notification
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
import google.generativeai as genai
import threading
from pydub import AudioSegment
from pydub.playback import play

# Set your Gemini API key
genai.configure(api_key="Gemini API Key")

# Initialize recognizer
recognizer = sr.Recognizer()

# Alert sound path
ALERT_SOUND_PATH = "121.mp3"  # Ensure this file exists in your directory

# Function to analyze mood
def detect_mood(frame):
    try:
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        emotion = result[0]['dominant_emotion']
        print("Detected Emotion:", emotion)
        return emotion
    except Exception as e:
        print("Error detecting emotion:", e)
        return None

# Function to play alert using pydub and simpleaudio
def play_alert():
    try:
        alert_sound = AudioSegment.from_file(ALERT_SOUND_PATH)
        play(alert_sound)
    except Exception as e:
        print("Error playing alert sound:", e)

# Function to show pop-up notification
def show_notification(msg):
    notification.notify(
        title="Mood Monitor Alert",
        message=msg,
        timeout=5
    )

# Chatbot voice response
def speak(text):
    tts = gTTS(text)
    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
        tts.save(fp.name)
        speech = AudioSegment.from_file(fp.name)
        play(speech)

# Chat with Gemini
def chat_with_gemini(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

# Start chatbot voice interaction
def voice_chat():
    while True:
        with sr.Microphone() as source:
            print("You can speak now...")
            audio = recognizer.listen(source)
            try:
                user_input = recognizer.recognize_google(audio)
                print("You said:", user_input)

                response = chat_with_gemini(user_input)
                print("Gemini:", response)
                speak(response)
            except Exception as e:
                print("Error in voice chat:", e)
                speak("Sorry, I couldn't understand.")

# Start the chatbot in a separate thread
chat_thread = threading.Thread(target=voice_chat)
chat_thread.daemon = True
chat_thread.start()

# Start webcam and detect emotion
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break

    mood = detect_mood(frame)
    if mood in ['angry', 'sad', 'tired', 'sleepy']:
        show_notification(f"You seem {mood}. Take a short break!")
        play_alert()

    # Display camera feed
    cv2.imshow("Mood Monitor", frame)

    if cv2.waitKey(5) & 0xFF == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()

