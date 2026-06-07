from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import setup_logging
from app.config.settings import settings
from app.core.database.session import close_db, init_db
from app.core.utils.response import Response
from app.modules.attachment.router import router as attachment_router
from app.modules.auth.router import router as auth_router
from app.modules.auth.service import auth_service
from app.modules.change.router import router as change_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.ai.mcp.router import router as ai_mcp_router
from app.modules.ai.model_manager.router import router as ai_model_router
from app.modules.ai.rag.router import router as ai_rag_router
from app.modules.ai.router import router as ai_router
from app.modules.ai.skill.router import router as ai_skill_router
from app.modules.audit.router import router as audit_router
from app.modules.demo.router import router as demo_router
from app.modules.dictionary.router import router as dictionary_router
from app.modules.git.router import router as git_router
from app.modules.knowledge.router import router as knowledge_router
from app.modules.upgrade.router import router as upgrade_router
from app.modules.wiki.router import router as wiki_router
from app.modules.jenkins.router import router as jenkins_router
from app.modules.organization.router import router as org_router
from app.modules.user.admin_router import router as user_admin_router
from app.modules.user.router import router as user_router


# 静态资源目录（头像上传等）
UPLOADS_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_db()
    created = await auth_service.ensure_admin_user("guoxudong", "1234", "Guo XuDong")
    if created:
        print("[GuiGraph] 管理员账号已创建: guoxudong / 1234")
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

# ── Router 注册 ──
app.include_router(auth_router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(user_router, prefix="/api/v1/user", tags=["用户"])
app.include_router(user_admin_router, prefix="/api/v1/user-admin", tags=["用户管理(管理员)"])
app.include_router(org_router, prefix="/api/v1/org", tags=["组织架构"])
app.include_router(jenkins_router, prefix="/api/v1/jenkins", tags=["Jenkins"])
app.include_router(git_router, prefix="/api/v1/git", tags=["Git"])
app.include_router(change_router, prefix="/api/v1/changes", tags=["变更管理"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["仪表盘"])
app.include_router(demo_router, prefix="/api/v1/demo", tags=["演示/测试数据"])
app.include_router(attachment_router, prefix="/api/v1/attachment", tags=["附件"])
app.include_router(upgrade_router, prefix="/api/v1/upgrades", tags=["升级管理"])
app.include_router(ai_router, prefix="/api/v1/ai", tags=["AI"])
app.include_router(ai_rag_router, prefix="/api/v1/ai/rag", tags=["AI RAG"])
app.include_router(ai_model_router, prefix="/api/v1/ai/models", tags=["AI 模型管理"])
app.include_router(ai_skill_router, prefix="/api/v1/ai/skills", tags=["AI 技能"])
app.include_router(ai_mcp_router, prefix="/api/v1/ai/mcp", tags=["AI MCP"])
app.include_router(knowledge_router, prefix="/api/v1/knowledge", tags=["知识库"])
app.include_router(audit_router, prefix="/api/v1/audit", tags=["审计日志"])
app.include_router(wiki_router, prefix="/api/v1/wiki", tags=["Wiki"])
app.include_router(dictionary_router, prefix="/api/v1/dictionary", tags=["数据字典"])

# 静态资源（头像等）
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")


# ── 全局异常处理器 ──

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_ERROR",
    }
    return JSONResponse(
        status_code=exc.status_code,
        content=Response.fail(
            message=str(exc.detail),
            code=code_map.get(exc.status_code, "ERROR"),
        ),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=Response.fail(
            message=str(exc.errors()),
            code="VALIDATION_ERROR",
        ),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=Response.fail(
            message="服务器内部错误",
            code="INTERNAL_ERROR",
        ),
    )


# ── 基础端点 ──

@app.get("/health")
async def health_check():
    return Response.ok({"status": "healthy", "app": settings.APP_NAME})


@app.get("/")
async def root():
    return Response.ok({"status": "ok", "message": f"Welcome to {settings.APP_NAME} API", "docs": "/docs"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=10011, reload=True)