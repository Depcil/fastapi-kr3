import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from database import init_db
from routers import auth, basic, db, todos
from security import docs_auth

load_dotenv()

MODE = os.getenv("MODE", "DEV")
if MODE not in ("DEV", "PROD"):
    raise ValueError(f"Недопустимое значение MODE: {MODE}. Допустимые: DEV, PROD")

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

init_db()

# --- 6.3: документация в зависимости от MODE ---
if MODE == "DEV":
    @app.get("/openapi.json", include_in_schema=False)
    def openapi_json(_: str = Depends(docs_auth)):
        return JSONResponse(get_openapi(title=app.title, version=app.version, routes=app.routes))

    @app.get("/docs", include_in_schema=False)
    def swagger(_: str = Depends(docs_auth)):
        return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")

elif MODE == "PROD":
    @app.get("/docs", include_in_schema=False)
    def docs_prod():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not Found")

    @app.get("/openapi.json", include_in_schema=False)
    def openapi_prod():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not Found")

# rate limiter
app.state.limiter = auth.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# подключаем роутеры
app.include_router(basic.legacy_router)   # 6.1
app.include_router(basic.router)          # 6.2
app.include_router(auth.router)           # 6.4, 6.5, 7.1
app.include_router(db.router)             # 8.1
app.include_router(todos.router)          # 8.2
