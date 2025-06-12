from utils.jwt_handler import JWTHandler
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends,HTTPException
security = HTTPBearer()

# Middleware / Dependency to extract and decode JWT token
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        user_data = JWTHandler.decode(token)
        return user_data
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
