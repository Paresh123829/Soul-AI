from flask import Flask, render_template, request, jsonify
import numpy as np
import cv2
from deepface import DeepFace
import threading
import simpleaudio as sa
import google.generativeai as genai
import io
import datetime
import os
from gtts import gTTS
from pydub import AudioSegment
import speech_recognition as sr
from flask import request, jsonify
from pydub import AudioSegment
import io

app = Flask(__name__)

# Initialize mood log as a global variable
mood_log = []

# Configure Gemini API
genai.configure(api_key="AIzaSyCO19-BFJxgNokSstOO30Iox2CRdo_TBfg")
model = genai.GenerativeModel("gemini-1.5-flash")

def play_alert():
    try:
        mp3_path = "121.mp3"
        wav_path = '121.wav'

        if not os.path.exists(wav_path):
            sound = AudioSegment.from_mp3(mp3_path)
            sound.export(wav_path, format="wav")

        wave_obj = sa.WaveObject.from_wave_file(wav_path)
        play_obj = wave_obj.play()
    except Exception as e:
        print("Audio alert error:", e)

def detect_mood(frame):
    try:
        result = DeepFace.analyze(img_path=frame, actions=['emotion'], enforce_detection=False)

        if isinstance(result, list):
            emotion = result[0]['dominant_emotion']
        else:
            emotion = result['dominant_emotion']

        return emotion
    except Exception as e:
        print("Detection error:", e)
        return "Unknown"

def mood_suggestion(mood):
    suggestions = {
        "angry": "Try deep breathing or a short walk.",
        "sad": "Play your favorite music or talk to a friend.",
        "fear": "Practice grounding techniques.",
        "disgust": "Take a short break and relax.",
        "happy": "Keep spreading that joy!",
        "surprise": "Take a moment to process things.",
        "neutral": "Stay mindful and focused."
    }
    return suggestions.get(mood.lower(), "Stay positive and take care!")

@app.route('/')
def index():
    return render_template('welcome.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/detect_mood', methods=['POST'])
def detect_mood_route():
    file = request.files.get('video_frame')
    if not file:
        return jsonify({'mood': 'No Frame Received'})

    try:
        in_memory_file = io.BytesIO()
        file.save(in_memory_file)
        data = np.frombuffer(in_memory_file.getvalue(), dtype=np.uint8)
        frame = cv2.imdecode(data, cv2.IMREAD_COLOR)

        if frame is None or frame.size == 0:
            return jsonify({'mood': 'Invalid Image'})

        # Capture multiple frames over 5 seconds (simulate from same image for now)
        mood_counts = {}
        for _ in range(5):  # Ideally, capture different frames 1 sec apart
            mood = detect_mood(frame)
            mood_counts[mood] = mood_counts.get(mood, 0) + 1

        # Find the most common mood
        most_common_mood = max(mood_counts, key=mood_counts.get)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mood_log.append({"time": timestamp, "mood": most_common_mood})

        if most_common_mood.lower() in ['angry', 'fear', 'disgust']:
            threading.Thread(target=play_alert).start()

        suggestion = mood_suggestion(most_common_mood)
        return jsonify({'mood': most_common_mood, 'suggestion': suggestion})
    except Exception as e:
        print("Error in mood detection route:", e)
        return jsonify({'mood': 'Error', 'message': str(e)})


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form.get('user_input')
    if not user_input:
        return jsonify({'response': 'Please enter a message.'})

    try:
        response = model.generate_content(user_input)
        bot_reply = response.text

        os.makedirs('static', exist_ok=True)
        tts = gTTS(text=bot_reply, lang='en')
        audio_path = "static/response.mp3"
        tts.save(audio_path)

        return jsonify({'response': bot_reply, 'audio': audio_path})
    except Exception as e:
        print("Chat error:", e)
        return jsonify({'response': f"Gemini error: {str(e)}", 'audio': ''})

@app.route('/voice_chat', methods=['POST'])
def voice_chat():
    if 'voice' not in request.files:
        return jsonify({'response': 'No audio received.'})

    voice_file = request.files['voice']
    
    try:
        # Attempt to convert the audio from the default browser format (e.g. webm)
        try:
            audio = AudioSegment.from_file(voice_file, format="webm")
        except Exception as e:
            # If reading as webm fails, try ogg (or adjust as needed)
            voice_file.seek(0)
            audio = AudioSegment.from_file(voice_file, format="ogg")

        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
        
        # Use SpeechRecognition to convert speech to text
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
            transcript = recognizer.recognize_google(audio_data)
        
        # Now that we have the transcript, send it to your Gemini model
        response = model.generate_content(transcript)
        bot_reply = response.text

        # Optionally, generate an audio file for the bot reply using gTTS
        tts = gTTS(text=bot_reply, lang='en')
        audio_path = "static/voice_response.mp3"
        tts.save(audio_path)
        
        return jsonify({
            'response': bot_reply,
            'audio': audio_path,
            'transcript': transcript
        })

    except Exception as e:
        print("Error during voice processing:", e)
        return jsonify({'response': f'Error processing audio: {str(e)}'})


@app.route('/mood_log', methods=['GET'])
def mood_history():
    return jsonify(mood_log)

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        # Print for debugging
        print("Received registration data:", data)

        # TODO: Save to DB (later we can connect SQLite or MongoDB)
        return jsonify({"message": "Registration successful"}), 200

    except Exception as e:
        print("Registration error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    if not os.path.exists("121.mp3"):
        print("Warning: Alert sound file '121.mp3' not found!")

    app.run(debug=True)

