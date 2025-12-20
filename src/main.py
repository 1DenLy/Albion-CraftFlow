from fastapi import FastAPI
from src.routers import locations, items, tracking, prices

app = FastAPI(title="Albion Market API")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Service is running"}


app.include_router(locations.router)
app.include_router(items.router)
app.include_router(tracking.router)
app.include_router(prices.router)