from fastapi import FastAPI
from src.db.models import Location
app = FastAPI(title="Albion Market API")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Service is running"}