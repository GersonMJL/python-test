from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.api.endpoints import files, users


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application
    """
    app = FastAPI(
        title="File Management API",
        description="API for managing file uploads and user data",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Include routers
    app.include_router(files.router, tags=["files"])
    app.include_router(users.router, tags=["users"])

    # Custom exception handlers
    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc):
        return JSONResponse(status_code=400, content={"message": str(exc)})

    @app.exception_handler(FileNotFoundError)
    async def file_not_found_handler(request, exc):
        return JSONResponse(status_code=404, content={"message": "File not found"})

    return app


# Create the application instance
app = create_application()
