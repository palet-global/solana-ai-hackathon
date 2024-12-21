from typing import Dict
from dataclasses import dataclass
from fastapi import HTTPException
from src.utils.is_validators import is_not_empty

@dataclass
class ErrorInfo:
    code: int
    message: str

class ErrorCodes:
    # Return 400 Bad Request for validation errors
    INVALID_REQUEST = ErrorInfo(
        code=400,
        message="The request was invalid or cannot be processed, often due to incorrect or missing request parameters."
    )
    
    # Return 409 Conflict for database conflicts
    CONFLICT_RESOURCE = ErrorInfo(
        code=409,
        message="The request could not be completed due to a conflict with the current state of the resource. This may occur if the resource already exists or if required data is missing."
    )
    
    # Return 500 Internal Server Error for unexpected errors
    INTERNAL_ERROR = ErrorInfo(
        code=500,
        message="An unexpected error occurred on the server. Please try again later or contact support if the issue persists."
    )

    # Return 503 Server Error for unexpected errors
    REQUEST_ERROR = ErrorInfo(
        code=503,
        message="The service is temporarily unavailable. Please try again later."
    )
    
    @classmethod
    def get_all_errors(cls) -> Dict[str, ErrorInfo]:
        return {
            name: value 
            for name, value in vars(cls).items() 
            if isinstance(value, ErrorInfo) and not name.startswith('_')
        }

# Raise HTTPException using our ErrorCodes class
def raise_HTTPException(error: ErrorInfo, message: str = ""):
    """
    Helper function to raise HTTPException with error code and message
    """
    # Lets establish the default error
    error_message = error.message

    # Lets check if there is a custom message
    if is_not_empty(message):
        error_message = message

    # Lets raise the Exception
    raise HTTPException(
        status_code=error.code,
        detail=error_message 
    )