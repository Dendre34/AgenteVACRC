from fastapi import FastAPI

from app.api.router import api_router
from app.core.exception_handler import register_exception
from app.core.log import set_custom_logfile, setup_logging
from app.core.response_schema import ResponseModel, response_base

setup_logging()
set_custom_logfile()

app = FastAPI(title="AgenteVACRC API", version="1.0.0")

app.include_router(api_router, prefix="/api/v1")

register_exception(app)


@app.get("/health", response_model=ResponseModel)
async def health_check() -> ResponseModel:
    return response_base.success(data={"status": "ok"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
