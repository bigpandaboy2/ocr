from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from core.database import init_models
from documents.routes import router as upload_router
from users.routes import router as guest_router, user_router
from auth.route import router as auth_router
from core.security import JWTAuth

from starlette.middleware.authentication import AuthenticationMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_models()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(upload_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(guest_router)

app.add_middleware(AuthenticationMiddleware, backend=JWTAuth())

@app.get("/")
def health_check():
    return JSONResponse(content={"message": "OK"})
