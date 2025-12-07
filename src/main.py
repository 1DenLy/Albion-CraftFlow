from fastapi import FastAPI
# Импортируем модули из новой папки
from src.routers import locations, items, tracking, prices

app = FastAPI(title="Albion Market API")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Service is running"}

# Подключаем роутеры
# Префиксы и теги уже определены внутри роутеров, здесь дублировать не нужно
app.include_router(locations.router)
app.include_router(items.router)
app.include_router(tracking.router)
app.include_router(prices.router)