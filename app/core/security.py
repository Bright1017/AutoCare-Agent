import os
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.config import settings

# Define the name of the API header the client must send
API_KEY_NAME = "AutoCare"

# Initialize the header extractor. auto_error=False lets and handles the error gracefully ourselves.
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def validate_api_key(api_key: str = Security(api_key_header)):
    """
    Pragmatic API Key validation dependency.
    Intercepts the request, checks the API-Key header, and blocks unauthorized traffic.
    """
    # i can also implement additional logic here, such as rate limiting, logging unauthorized attempts, or even integrating with a more complex auth system if needed in the future.
    expected_key = settings.APP_API_KEY
    
    # this will catch the case where the server is misconfigured and the master API key is not set, preventing any access to the API and prompting the admin to fix the configuration. It also prevents a potential security loophole where an empty or null key might be accepted if not properly checked.
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="API security key is unconfigured on the server."
        )
        
    # If the visitor's key doesn't match the master key, kick them out instantly
    if api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid or missing API-Key header."
        )
        
    # This will stamp the request as authorized and wave them through
    return api_key