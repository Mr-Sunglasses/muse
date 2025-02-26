# tests/test_main.py

import io
import os

import pytest
from fastapi.testclient import TestClient

from src.muse.main import UPLOAD_DIR, app, get_settings

client = TestClient(app)


def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert "Coldplay" in response.text


def test_upload_invalid_secret():
    audio_content = b"RIFF....WAVEfmt..."  # fake WAV header
    file = {"file": ("test.wav", io.BytesIO(audio_content), "audio/wav")}
    data = {"secret_phrase": "wrong_phrase"}
    response = client.post("/upload/", data=data, files=file)
    assert response.status_code == 200
    assert "Invalid secret phrase" in response.text


def test_upload_valid_file(tmp_path):
    # Patch upload dir
    test_file = tmp_path / "test.mp3"
    test_file.write_bytes(b"ID3")  # Fake MP3 file

    with open(test_file, "rb") as f:
        file = {"file": ("test.mp3", f, "audio/mpeg")}
        data = {"secret_phrase": get_settings().SECRET_PHRASE}
        response = client.post("/upload/", data=data, files=file)
        assert response.status_code == 200
        assert "test.mp3" in response.text

    # Clean up uploaded file
    uploaded_path = os.path.join(UPLOAD_DIR, "test.mp3")
    if os.path.exists(uploaded_path):
        os.remove(uploaded_path)
