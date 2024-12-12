from typing import Optional

from fastapi import APIRouter
from fastapi import Response, Query
from fastapi.responses import JSONResponse

from src.services.file_management_service import FileManagementService

router = APIRouter()


@router.get("/max-size/")
async def max_size(file_name: str):
    """
    Get maximum file size.

    Args:
        file_name (str): Name of the file

    Returns:
        Response with max size
    """
    try:
        result = FileManagementService.get_size(file_name, "max")
        return Response(content=result, status_code=200)
    except FileNotFoundError:
        return Response(content="File not found", status_code=404)


@router.get("/min-size/")
async def min_size(file_name: str):
    """
    Get minimum size.

    Args:
        file_name (str): Name of the file

    Returns:
        Response with min size
    """
    try:
        result = FileManagementService.get_size(file_name, "min")
        return Response(content=result, status_code=200)
    except FileNotFoundError:
        return Response(content="File not found", status_code=404)


@router.get("/list-users/")
async def list_users(
    file_name: str,
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0),
    name: Optional[str] = Query(None),
    order: str = Query("asc", regex="^(asc|desc)$"),
):
    """
    List users with filtering and pagination.

    Args:
        file_name (str): Name of the file
        page (int): Page number
        limit (int): Number of users per page
        name (Optional[str]): Filter by name
        order (str): Sort order

    Returns:
        JSONResponse with list of users
    """
    try:
        users = FileManagementService.list_users(file_name, page, limit, name, order)
        return JSONResponse(content=users, status_code=200)
    except FileNotFoundError:
        return Response(content="File not found", status_code=404)


@router.get("/list-users-range/")
async def list_users_range(
    file_name: str,
    min_val: int = Query(..., alias="min"),
    max_val: int = Query(..., alias="max"),
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0),
    name: Optional[str] = Query(None),
):
    """
    List users within a specific message count range.

    Args:
        file_name (str): Name of the file
        min_val (int): Minimum message count
        max_val (int): Maximum message count
        page (int): Page number
        limit (int): Number of users per page
        name (Optional[str]): Filter by name

    Returns:
        JSONResponse with list of users
    """
    try:
        users = FileManagementService.list_users(
            file_name, page, limit, name, min_val=min_val, max_val=max_val
        )
        return JSONResponse(content=users, status_code=200)
    except FileNotFoundError:
        return Response(content="File not found", status_code=404)
