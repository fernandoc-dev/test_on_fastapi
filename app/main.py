"""
Main FastAPI application
"""
from fastapi import FastAPI
from app.routers import users

app = FastAPI(
    title="FastAPI Test Template",
    description="Modular and reusable testing template for FastAPI",
    version="1.0.0"
)

# Include routers
app.include_router(users.router)


@app.get("/")
async def root():
    """Root endpoint - Hello World"""
    return {"message": "Hello World"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

