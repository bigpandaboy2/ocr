from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from core.database import init_models
from users.routes import router as user_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_models()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(user_router)

@app.get("/")
def health_check():
    return JSONResponse(content={"message": "OK"})
