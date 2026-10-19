"""ClaimPilot prototype upload router. Requires authentication before production."""
from pathlib import Path
from uuid import uuid4
import os

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

router = APIRouter(prefix="/claims", tags=["Claim documents"])
STORAGE = Path(os.environ.get("CLAIMPILOT_UPLOAD_DIR", "./private_uploads")).resolve()
MAX_BYTES = 10 * 1024 * 1024
CHUNK_BYTES = 1024 * 1024
ALLOWED = {
    "image/jpeg": (".jpg", ".jpeg"),
    "image/png": (".png",),
    "image/webp": (".webp",),
    "application/pdf": (".pdf",),
}


def matches_signature(content_type: str, header: bytes) -> bool:
    if content_type == "image/jpeg":
        return header.startswith(b"\xff\xd8\xff")
    if content_type == "image/png":
        return header.startswith(b"\x89PNG\r\n\x1a\n")
    if content_type == "image/webp":
        return header.startswith(b"RIFF") and header[8:12] == b"WEBP"
    if content_type == "application/pdf":
        return header.startswith(b"%PDF-")
    return False


@router.post("/{claim_id}/documents", status_code=201)
async def upload_document(
    claim_id: str,
    category: str = Form(...),
    file: UploadFile = File(...),
):
    # PROTOTYPE ONLY: replace with authenticated claim ownership checks.
    if not claim_id or len(claim_id) > 64 or not all(c.isalnum() or c in "-_" for c in claim_id):
        raise HTTPException(400, "Invalid claim ID")
    if category not in {"accident_photo", "police_report", "repair_estimate"}:
        raise HTTPException(400, "Invalid document category")
    content_type = file.content_type or ""
    suffix = Path(file.filename or "").suffix.lower()
    if content_type not in ALLOWED or suffix not in ALLOWED[content_type]:
        raise HTTPException(415, "Only JPG, PNG, WebP, and PDF files are supported")

    header = await file.read(16)
    if not matches_signature(content_type, header):
        raise HTTPException(415, "File contents do not match the declared type")
    await file.seek(0)

    STORAGE.mkdir(mode=0o700, parents=True, exist_ok=True)
    destination_dir = STORAGE / claim_id
    destination_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    file_id = uuid4().hex
    destination = destination_dir / (file_id + suffix)
    size = 0
    try:
        with destination.open("xb") as out:
            os.chmod(destination, 0o600)
            while chunk := await file.read(CHUNK_BYTES):
                size += len(chunk)
                if size > MAX_BYTES:
                    raise HTTPException(413, "Maximum upload size is 10 MB")
                out.write(chunk)
        return {"claim_id": claim_id, "file_id": file_id, "category": category,
                "content_type": content_type, "size_bytes": size, "status": "uploaded"}
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()
