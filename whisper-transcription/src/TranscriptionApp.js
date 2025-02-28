import React, { useState } from "react";
import axios from "axios";

const TranscriptionApp = () => {
    const [file, setFile] = useState(null);
    const [transcription, setTranscription] = useState("");
    const [loading, setLoading] = useState(false);
    const [downloadLink, setDownloadLink] = useState("");

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) {
            alert("Please select a file first.");
            return;
        }

        setLoading(true);
        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            setTranscription(response.data.transcription);
            setDownloadLink(response.data.file);
        } catch (error) {
            console.error("Error uploading file:", error);
            alert("Failed to transcribe file.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <h2>Whisper Transcription</h2>
            <input type="file" onChange={handleFileChange} accept="audio/*,video/*" />
            <button onClick={handleUpload} disabled={loading}>
                {loading ? "Transcribing..." : "Upload & Transcribe"}
            </button>

            {transcription && (
                <div className="transcription-box">
                    <h3>Transcription:</h3>
                    <p>{transcription}</p>
                </div>
            )}

            {downloadLink && (
                <a href={`http://127.0.0.1:5000/download/${downloadLink.split('/').pop()}`} download>
                    Download Transcription
                </a>
            )}
        </div>
    );
};

export default TranscriptionApp;
