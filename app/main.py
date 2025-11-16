"""
Main FastAPI application
"""
from fastapi import FastAPI

app = FastAPI(
    title="FastAPI Test Template",
    description="Modular and reusable testing template for FastAPI",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Root endpoint - Hello World"""
    return {"message": "Hello World"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

