"""
Request validation middleware.
"""

from fastapi import Request, HTTPException
from typing import Any, Dict
import json


class ValidationMiddleware:
    """Middleware for request validation."""
    
    def __init__(self, max_request_size: int = 10 * 1024 * 1024):  # 10MB
        self.max_request_size = max_request_size
        
    async def __call__(self, request: Request, call_next):
        """Process and validate request."""
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            raise HTTPException(status_code=413, detail="Request too large")
            
        response = await call_next(request)
        return response


def validate_request_data(data: Dict[str, Any], required_fields: list[str]) -> bool:
    """
    Validate that required fields are present in request data.
    
    Args:
        data: Request data dictionary
        required_fields: List of required field names
        
    Returns:
        True if valid
        
    Raises:
        HTTPException if validation fails
    """
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )
        
    return True
