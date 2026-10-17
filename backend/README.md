# ClaimPilot Photo & Document Uploads — Prototype

## Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` to try the endpoint.

`POST /claims/{claim_id}/documents` accepts multipart form fields:
- `category`: `accident_photo`, `police_report`, or `repair_estimate`
- `file`: JPG, PNG, WebP, or PDF, max 10 MB

Example:

```bash
curl -X POST 'http://127.0.0.1:8000/claims/demo-001/documents' \
  -F 'category=accident_photo' -F 'file=@accident.jpg'
```

To add to an existing FastAPI app, import and call `app.include_router(uploads_router)`.

## Before real customer use

**This is a development prototype, not production-safe for insurance data.** Add user authentication and per-claim authorization; malware scanning and robust file parsing; encrypted private object storage; database records for files and claims; audit logging; retention and deletion policies; upload rate limits; storage quotas; and legal/compliance review. File signatures alone cannot establish that an upload is safe. Do not expose the upload directory publicly or use actual policyholder information while testing.
