"""
NASA API endpoints.

These endpoints expose NASA API data through our FastAPI application.
Following Clean Architecture: routers depend on use cases, not repositories.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
import httpx

from app.schemas.nasa import APOD
from app.application.nasa.use_cases import GetAPODUseCase
from app.application.nasa.dependencies import get_apod_use_case


router = APIRouter(prefix="/nasa", tags=["nasa"])


@router.get("/apod", response_model=APOD, status_code=status.HTTP_200_OK)
async def get_apod(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format. Defaults to today."),
    hd: bool = Query(False, description="Return HD image URL if available."),
    use_case: GetAPODUseCase = Depends(get_apod_use_case)
):
    """
    Get Astronomy Picture of the Day (APOD) from NASA API.
    
    This endpoint consumes the NASA APOD API endpoint:
    https://api.nasa.gov/planetary/apod
    
    Args:
        date: Optional date in YYYY-MM-DD format. If not provided, returns today's APOD.
        hd: Whether to return HD image URL if available.
        use_case: GetAPODUseCase instance (injected via dependency)
        
    Returns:
        APOD object containing:
        - date: Date of the APOD
        - explanation: Explanation of the image
        - title: Title of the image
        - media_type: Type of media (image or video)
        - service_version: API version
        - url: URL of the image/video
        - hdurl: HD URL (if hd=True and available)
        
    Raises:
        HTTPException: 
            - 500 if NASA API fails
            - 400 if date format is invalid or other API error
    """
    try:
        apod = await use_case.execute(date=date, hd=hd)
        return apod
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid request to NASA API: {str(e)}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching APOD from NASA API: {str(e)}"
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error connecting to NASA API: {str(e)}"
        )

