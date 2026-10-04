from fastapi import FastAPI
from sqlalchemy import text

from .database import engine

app = FastAPI(
    title="ORBIT-X",
    description="Autonomous Cyber Defense & Digital Twin for Space Systems",
    version="0.1.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "project": "ORBIT-X",
        "status": "online",
        "version": "0.1.0",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
    }


@app.get("/health/database")
def database_health() -> dict[str, str]:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "database": "connected",
        "status": "healthy",
    }