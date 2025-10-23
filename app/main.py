from fastapi import FastAPI
from app.api import users, enterprises, roles, auth, auth_otp, telegram, workflow, dictionaries, audit_plans, auditor_qualifications, audits, audit_components, findings, attachments, settings, integrations, change_history

app = FastAPI(
    title="MGC Audits API",
    description="API для системы управления аудитами качества и несоответствиями",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(auth_otp.router, prefix="/api/v1")
app.include_router(telegram.router, prefix="/api/v1")
app.include_router(workflow.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(enterprises.router, prefix="/api/v1")
app.include_router(roles.router, prefix="/api/v1")
app.include_router(dictionaries.router, prefix="/api/v1")
app.include_router(audit_plans.router, prefix="/api/v1")
app.include_router(auditor_qualifications.router, prefix="/api/v1")
app.include_router(audits.router, prefix="/api/v1")
app.include_router(audit_components.router, prefix="/api/v1")
app.include_router(findings.router, prefix="/api/v1")
app.include_router(attachments.router, prefix="/api/v1")
app.include_router(settings.router, prefix="/api/v1")
app.include_router(integrations.router, prefix="/api/v1")
app.include_router(change_history.router, prefix="/api/v1")


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

