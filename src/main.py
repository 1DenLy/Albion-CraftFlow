from fastapi import FastAPI

app = FastAPI(title="Albion Market API")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Service is running"}