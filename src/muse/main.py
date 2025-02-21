import os
import shutil
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings, SettingsConfigDict


# Setup env variables
class Settings(BaseSettings):
    SECRET_PHRASE: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()


app = FastAPI()

BASE_DIR = Path(__file__).parent

TEMPLATES_DIR = BASE_DIR / "templates"

STATIC_DIR = BASE_DIR / "static"

UPLOAD_DIR = STATIC_DIR / "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

SECRET_PHRASE = get_settings().SECRET_PHRASE

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, error: str = None):
    music_files = os.listdir(UPLOAD_DIR)
    return templates.TemplateResponse(
        "index.html", {"request": request, "music_files": music_files, "error": error}
    )


@app.post("/upload/")
async def upload_music(
    request: Request, file: UploadFile = File(...), secret_phrase: str = Form(...)
):
    if secret_phrase != SECRET_PHRASE:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "music_files": os.listdir(UPLOAD_DIR),
                "error": "Invalid secret phrase!",
            },
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return RedirectResponse("/", status_code=303)
