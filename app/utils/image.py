"""Image upload validation and safe file storage."""
import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def validate_image(file: UploadFile) -> str:
    """Validate an uploaded image file. Returns a safe filename or raises HTTPException."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # Read content to check size
    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Image too large (max 5 MB)")

    # Reset file pointer for later reads
    file.file.seek(0)

    safe_name = f"{uuid.uuid4().hex}{ext}"
    return safe_name


def save_uploaded_image(file: UploadFile, upload_dir: Path, url_prefix: str = "/static/uploads") -> str:
    """Validate and save an uploaded image. Returns the URL path to the saved file."""
    safe_name = validate_image(file)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / safe_name
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return f"{url_prefix}/{safe_name}"
