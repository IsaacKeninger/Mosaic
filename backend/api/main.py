"""FastAPI app for local development. Mirrors the Lambda routes 1:1."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import classify, personas, plaid

app = FastAPI(title="Mosaic API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plaid.router, prefix="/sync", tags=["plaid"])
app.include_router(classify.router, prefix="/classify", tags=["classify"])
app.include_router(personas.router, prefix="/persona", tags=["personas"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
