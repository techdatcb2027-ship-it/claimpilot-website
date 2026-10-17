from fastapi import FastAPI
from uploads import router as uploads_router

app = FastAPI(title="ClaimPilot Document Uploads")
app.include_router(uploads_router)
