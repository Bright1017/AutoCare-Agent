import os
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

# Define the name of the header the client must send
API_KEY_NAME = "AutoCare"

# Initialize the header extractor. auto_error=False lets us handle the error gracefully ourselves.
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def validate_api_key(api_key: str = Security(api_key_header)):
    """
    Pragmatic API Key validation dependency.
    Intercepts the request, checks the X-API-Key header, and blocks unauthorized traffic.
    """
    # Grab the master secret password you set in your Railway environment variables
    expected_key = os.getenv("APP_API_KEY")
    
    # Safety Check: If you forgot to configure the key on Railway, sound the alarm
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="API security key is unconfigured on the server."
        )
        
    # Guard Check: If the visitor's key doesn't match your master key, kick them out instantly
    if api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid or missing X-API-Key header."
        )
        
    # Success: Stamp the request as authorized and wave them through
    return api_key