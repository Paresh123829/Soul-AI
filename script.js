document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const webcamElement = document.getElementById('webcam');
    const startDetectionBtn = document.getElementById('start-detection');
    const currentMoodElement = document.getElementById('current-mood');
    const moodSuggestionElement = document.getElementById('mood-suggestion');
    const userInputElement = document.getElementById('user-input');
    const sendMessageBtn = document.getElementById('send-message');
    const voiceInputBtn = document.getElementById('voice-input');
    const chatMessagesElement = document.getElementById('chat-messages');
    const playAudioBtn = document.getElementById('play-audio');
    const showHistoryBtn = document.getElementById('show-history');
    const moodHistoryElement = document.getElementById('mood-history');
    const historyTbodyElement = document.getElementById('history-tbody');

    let stream = null;
    let detectionInterval = null;
    let lastAudioUrl = null;
    let isDetectionRunning = false;

    // Webcam setup
    async function setupWebcam() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: false
            });
            webcamElement.srcObject = stream;
            return true;
        } catch (error) {
            console.error("Error accessing webcam:", error);
            currentMoodElement.textContent = "Webcam access denied";
            return false;
        }
    }

    startDetectionBtn.addEventListener('click', function () {
        if (isDetectionRunning) {
            stopDetection();
        } else {
            startDetection();
        }
    });

    async function startDetection() {
        const webcamSuccess = await setupWebcam();
        if (!webcamSuccess) return;

        isDetectionRunning = true;
        startDetectionBtn.innerHTML = '<i class="fas fa-stop"></i> Stop Detection';
        detectionInterval = setInterval(detectMood, 1000);
    }

    function stopDetection() {
        isDetectionRunning = false;
        startDetectionBtn.innerHTML = '<i class="fas fa-play"></i> Start Detection';

        if (detectionInterval) clearInterval(detectionInterval);
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            webcamElement.srcObject = null;
        }

        currentMoodElement.textContent = "Detection stopped";
        moodSuggestionElement.textContent = "";
    }

    async function detectMood() {
        try {
            const canvas = document.createElement('canvas');
            canvas.width = webcamElement.videoWidth;
            canvas.height = webcamElement.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(webcamElement, 0, 0);

            canvas.toBlob(async (blob) => {
                const formData = new FormData();
                formData.append('video_frame', blob, 'frame.jpg');

                const response = await fetch('/detect_mood', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                updateMoodDisplay(data.mood, data.suggestion);
            }, 'image/jpeg');
        } catch (error) {
            console.error("Error during mood detection:", error);
            currentMoodElement.textContent = "Detection error";
            moodSuggestionElement.textContent = "";
        }
    }

    function updateMoodDisplay(mood, suggestion) {
        currentMoodElement.className = '';
        const moodClass = `mood-${mood.toLowerCase()}`;
        currentMoodElement.classList.add(moodClass);
        currentMoodElement.textContent = mood.charAt(0).toUpperCase() + mood.slice(1);
        moodSuggestionElement.textContent = suggestion || "";
    }

    sendMessageBtn.addEventListener('click', sendMessage);
    userInputElement.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') sendMessage();
    });

    async function sendMessage(message = null) {
        const input = message || userInputElement.value.trim();
        if (!input) return;

        addMessageToChat('user', input);
        userInputElement.value = '';

        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot';
        typingDiv.innerHTML = '<div class="message-content">Typing...</div>';
        chatMessagesElement.appendChild(typingDiv);
        chatMessagesElement.scrollTop = chatMessagesElement.scrollHeight;

        try {
            const formData = new FormData();
            formData.append('user_input', input);

            const response = await fetch('/chat', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            chatMessagesElement.removeChild(typingDiv);
            addMessageToChat('bot', data.response);

            if (data.audio) {
                lastAudioUrl = data.audio;
                playAudioBtn.disabled = false;
            } else {
                lastAudioUrl = null;
                playAudioBtn.disabled = true;
            }
        } catch (error) {
            console.error("Chat error:", error);
            addMessageToChat('bot', "Sorry, I'm having trouble connecting to the server.");
        }
    }

    function addMessageToChat(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.innerHTML = `<div class="message-content">${message}</div>`;
        chatMessagesElement.appendChild(messageDiv);
        chatMessagesElement.scrollTop = chatMessagesElement.scrollHeight;
    }

    playAudioBtn.addEventListener('click', function () {
        if (lastAudioUrl) {
            const audio = new Audio(lastAudioUrl);
            audio.play();
        }
    });

    showHistoryBtn.addEventListener('click', async function () {
        const isHidden = moodHistoryElement.classList.contains('hidden');

        if (isHidden) {
            try {
                const response = await fetch('/mood_log');
                const data = await response.json();

                historyTbodyElement.innerHTML = '';
                data.forEach(entry => {
                    const row = document.createElement('tr');
                    row.innerHTML = `<td>${entry.time}</td><td class="mood-${entry.mood.toLowerCase()}">${entry.mood}</td>`;
                    historyTbodyElement.appendChild(row);
                });

                moodHistoryElement.classList.remove('hidden');
                showHistoryBtn.innerHTML = '<i class="fas fa-eye-slash"></i> Hide History';
            } catch (error) {
                console.error("Mood history error:", error);
                alert("Could not load mood history.");
            }
        } else {
            moodHistoryElement.classList.add('hidden');
            showHistoryBtn.innerHTML = '<i class="fas fa-history"></i> View History';
        }
    });

    // 🎤 Voice input button using MediaRecorder API for actual audio recording
    voiceInputBtn.addEventListener('click', async () => {
        if (!('MediaRecorder' in window)) {
            alert('Audio recording is not supported in this browser.');
            return;
        }

        try {
            // Request access to the microphone
            const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const recorder = new MediaRecorder(audioStream);
            let audioChunks = [];

            // Set UI feedback for recording
            voiceInputBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

            // Collect audio data
            recorder.ondataavailable = event => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            // When recording stops, send the audio to the backend
            recorder.onstop = async () => {
                // Create a blob using the recorded audio; we record in the default format (e.g., webm)
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const formData = new FormData();
                formData.append('voice', audioBlob, 'recording.webm');

                try {
                    const response = await fetch('/voice_chat', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await response.json();
                    
                    // Add the user's transcript to the chat if available
                    if(data.transcript) {
                        addMessageToChat('user', data.transcript);
                    }
                    // Then add the bot's reply
                    addMessageToChat('bot', data.response);

                    if (data.audio) {
                        lastAudioUrl = data.audio;
                        playAudioBtn.disabled = false;
                    }
                } catch (err) {
                    console.error('Voice chat error:', err);
                    addMessageToChat('bot', "Sorry, there was a problem processing your voice.");
                }
                // Reset the voice input button icon
                voiceInputBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            };

            // Start recording and stop after a fixed duration (e.g., 3 seconds)
            recorder.start();
            setTimeout(() => {
                recorder.stop();
            }, 3000);

        } catch (err) {
            console.error('Error accessing microphone:', err);
            alert('Microphone access denied.');
            voiceInputBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        }
    });

    window.addEventListener('beforeunload', function () {
        if (detectionInterval) clearInterval(detectionInterval);
        if (stream) stream.getTracks().forEach(track => track.stop());
    });
});
