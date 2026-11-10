from app.config import settings

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path


def setup_mount_point(_app: FastAPI) -> None:
    # BASE_DIR = Path(__file__).parent.parent.parent
    # STATIC_DIR = BASE_DIR / "static"

    # UPLOAD_DIR = Path(settings.upload_dir)
    # UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    upload_dir_name = settings.upload_dir
    _app.mount("/static", StaticFiles(directory="static"), name="static")
    _app.mount(f"/{upload_dir_name}", StaticFiles(directory=upload_dir_name), name=upload_dir_name)
