from fastapi import FastAPI

app = FastAPI(
    title="MGC Audits API",
    description="API для системы управления аудитами качества и несоответствиями",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.get("/")
async def root():
    return {
        "message": "MGC Audits API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}

