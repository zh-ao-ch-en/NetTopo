"""FastAPI 应用入口。"""
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import models  # noqa: F401  确保模型注册到 Base.metadata
from app.api import auth, devices, monitor, topology, users
from app.config import CORS_ORIGINS
from app.database import Base, SessionLocal, engine
from app.response import fail, ok
from app.seed import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_if_empty(db)
    yield


app = FastAPI(title="网络实验室拓扑与设备管理系统 API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=fail(exc.status_code, str(exc.detail)),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content=fail(422, "请求参数错误"))


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(status_code=500, content=fail(500, "服务器内部错误"))


app.include_router(auth.router)
app.include_router(devices.router)
app.include_router(topology.router)
app.include_router(monitor.router)
app.include_router(users.router)


@app.get("/api/health")
def health():
    return ok({"status": "ok"})