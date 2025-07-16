from fastapi import FastAPI
from routers import keys_router, health_router
from routers.keys import validate_public_key
from models.responses import ValidationResponse
from utils.key_loader import load_registered_public_keys

app = FastAPI(
    title="Sensor Key Registry",
    description="API service to validate public keys against registered sensor keys",
    version="1.0.0"
)

# Include routers
app.include_router(health_router)
app.include_router(keys_router)

app.post("/validate", response_model=ValidationResponse)(validate_public_key)


@app.on_event("startup")
async def startup_event():
    """Load registered keys on startup."""
    registered_keys = load_registered_public_keys()
    app.state.registered_keys = registered_keys
    print(
        f"[KeyRegistry] Loaded {len(registered_keys)} registered public keys")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
