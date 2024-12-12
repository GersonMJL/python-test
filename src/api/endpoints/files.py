from fastapi import APIRouter, File, UploadFile, Query
from fastapi.responses import JSONResponse
from typing import List
from src.services.file_management_service import FileManagementService

router = APIRouter()


@router.put("/upload", status_code=201)
async def upload_file(
    file: UploadFile = File(
        ..., description="File to be uploaded", media_type="multipart/form-data"
    )
):
    """
    Upload a file to the temporary storage.

    Args:
        file (UploadFile): File to be uploaded

    Returns:
        JSONResponse with upload status
    """
    try:
        status_code = FileManagementService.upload_file(file)
        return JSONResponse(
            content={"message": "File uploaded successfully"}, status_code=status_code
        )
    except ValueError as e:
        raise ValueError(str(e))


@router.get("/list", response_model=List[str])
async def list_files(
    page: int = Query(1, gt=0, description="Page number"),
    limit: int = Query(10, gt=0, le=100, description="Number of files per page"),
):
    """
    List files with pagination.

    Args:
        page (int): Page number
        limit (int): Number of files per page

    Returns:
        List of file names
    """
    return FileManagementService.list_files(page, limit)
