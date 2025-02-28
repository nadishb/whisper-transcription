import os
import whisper
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from moviepy import VideoFileClip

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Configure upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load Whisper model (Choose from 'tiny', 'base', 'small', 'medium', 'large')
model = whisper.load_model("base")

# Allowed file types
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".mp4", ".mkv", ".mov", ".flv", ".aac", ".m4a"}

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

def extract_audio(video_path):
    """Extracts audio from a video file and saves it as a WAV file."""
    audio_path = video_path.rsplit(".", 1)[0] + ".wav"
    if not os.path.exists(audio_path):  # Avoid redundant processing
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, codec="pcm_s16le")
    return audio_path

def transcribe_audio(audio_path):
    """Transcribes an audio file using Whisper and returns the text."""
    result = model.transcribe(audio_path)
    return result["text"]

@app.route("/upload", methods=["POST"])
def upload_file():
    """Handles file uploads and transcriptions."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file format"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    # If video, extract audio
    if file_path.lower().endswith((".mp4", ".mkv", ".mov", ".flv")):
        file_path = extract_audio(file_path)  # Convert to WAV before transcribing

    # Transcribe audio
    transcription = transcribe_audio(file_path)

    # Save transcription as text file
    transcript_path = file_path.rsplit(".", 1)[0] + ".txt"
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(transcription)

    return jsonify({"message": "Transcription completed!", "transcription": transcription, "file": transcript_path})

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    """Allows users to download the transcription file."""
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
