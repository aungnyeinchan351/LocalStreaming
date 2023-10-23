from flask import Flask, Response, render_template
import cv2
import pyaudio
import socket

app = Flask(__name__)

# Initialize the video capture
video_capture = cv2.VideoCapture(0)

# Initialize audio streaming
CHUNK = 1024
p = pyaudio.PyAudio()
audio_stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=CHUNK)

def generate_video():
    while True:
        success, frame = video_capture.read()
        if not success:
            continue
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

def generate_audio():
    while True:
        audio_data = audio_stream.read(CHUNK)
        yield (b'--frame\r\n' b'Content-Type: audio/wav\r\n\r\n' + audio_data + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/audio_feed')
def audio_feed():
    return Response(generate_audio(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host=socket.gethostbyname(socket.gethostname()), port=5000, debug=True)
