from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import setup_logging
from app.config.settings import settings
from app.core.database.session import close_db, init_db
from app.modules.auth.router import router as auth_router
from app.modules.auth.service import auth_service
from app.modules.user.router import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_db()
    created = await auth_service.ensure_admin_user("guoxudong", "1", "郭旭东")
    if created:
        print("[GuiGraph] 管理员账号已创建: guoxudong / 1")
    yield
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    description="版本变更管理系统 API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(user_router, prefix="/api/v1/user", tags=["用户"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=10011, reload=True)