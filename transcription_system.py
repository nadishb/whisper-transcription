import os
import time
import whisper
from moviepy import VideoFileClip
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define supported media formats
SUPPORTED_FORMATS = (".mp3", ".wav", ".mp4", ".mkv", ".mov", ".flv", ".aac", ".m4a")
DIRECTORY_TO_WATCH = r"C:\Users\bnadi\OneDrive\Desktop\python intern\media"  

model = whisper.load_model("base")

def get_media_files(directory):
    """Recursively fetch all supported media files in the directory."""
    media_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(SUPPORTED_FORMATS):
                media_files.append(os.path.join(root, file))
    return media_files

def extract_audio(video_path):
    """Extracts audio from a video file and saves it as a WAV file."""
    audio_path = video_path.rsplit(".", 1)[0] + ".wav"
    if not os.path.exists(audio_path):  # Avoid redundant processing
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, codec="pcm_s16le")
    return audio_path

def transcribe_audio(audio_path):
    """Transcribes an audio file using Whisper and saves the text file."""
    transcript_path = audio_path.rsplit(".", 1)[0] + ".txt"
    
    if os.path.exists(transcript_path):
        print(f"Skipping {audio_path}, already transcribed.")
        return

    print(f"Transcribing: {audio_path} ...")
    result = model.transcribe(audio_path)

    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(result["text"])

    print(f"Transcription saved: {transcript_path}")

def process_file(file_path):
    """Handles file processing by extracting audio (if needed) and transcribing."""
    if file_path.lower().endswith((".mp4", ".mkv", ".mov", ".flv")):
        file_path = extract_audio(file_path)  
    
    transcribe_audio(file_path)

class MediaFileHandler(FileSystemEventHandler):
    """Handles new media file events and triggers transcription."""
    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        if file_path.lower().endswith(SUPPORTED_FORMATS):
            print(f"New file detected: {file_path}")
            process_file(file_path)

def monitor_directory(directory):
    """Monitors the directory for new media files."""
    print(f"Monitoring directory: {directory}")
    event_handler = MediaFileHandler()
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(5)  
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    print("Scanning for existing media files...")
    media_files = get_media_files(DIRECTORY_TO_WATCH)
    
    for file in media_files:
        process_file(file)  
    
    print("Starting real-time monitoring...")
    monitor_directory(DIRECTORY_TO_WATCH)  
