from __future__ import annotations

import tempfile
from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile


app = FastAPI(
    title="Energy Bill Upload API",
    description="Accepts utility bill PDFs and stores them temporarily for downstream OCR processing.",
    version="1.0.0",
)

UPLOAD_DIR = Path(tempfile.gettempdir()) / "energy-bill-analyzer-uploads"


def trigger_ocr_placeholder(file_id: str, saved_path: str) -> None:
    """
    Placeholder hook for the OCR pipeline from Task 1.
    In the real system this could enqueue a background job instead of doing work inline.
    """
    _ = (file_id, saved_path)


def ensure_upload_directory() -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return UPLOAD_DIR


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload-bill")
async def upload_bill(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> dict[str, str]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name was provided.")

    original_name = Path(file.filename).name
    if Path(original_name).suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    if file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must be sent with a PDF content type.",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if not file_bytes.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF.")

    file_id = uuid4().hex
    upload_dir = ensure_upload_directory()
    stored_name = f"{file_id}.pdf"
    destination = upload_dir / stored_name

    try:
        destination.write_bytes(file_bytes)
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail="The server could not save the uploaded file.",
        ) from exc
    finally:
        await file.close()

    background_tasks.add_task(trigger_ocr_placeholder, file_id, str(destination))

    return {
        "message": "Utility bill uploaded successfully.",
        "file_id": file_id,
        "original_filename": original_name,
        "stored_filename": stored_name,
        "temporary_path": str(destination),
        "ocr_status": "placeholder trigger queued",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
