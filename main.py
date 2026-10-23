import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles

from common.discovery import discover_routers
from common.exception_handler import setup_exception_handlers
from database import database_lifespan
from settings import settings

# 文档页资源改用本地静态文件托管，避免访问公网 CDN 失败导致 SwaggerUIBundle is not defined
app = FastAPI(title=settings.app_name, lifespan=database_lifespan,
              docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Docs",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-dist/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui-dist/swagger-ui.css",
        swagger_favicon_url="/static/swagger-ui-dist/favicon-32x32.png",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

# 异常处理要先注册，CORS 中间件后注册，这样异常响应也会带上跨域响应头
setup_exception_handlers(app)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
    max_age=3600,
)

for router in discover_routers():
    app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
