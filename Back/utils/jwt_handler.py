import jwt
from datetime import datetime, timedelta
from typing import Any, Dict

class JWTHandler:
    SECRET_KEY = "NORM_MACDONALD"
    ALGORITHM = "HS256"
    EXPIRATION_MINUTES = 60  # default expiration

    @staticmethod
    def encode(data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=JWTHandler.EXPIRATION_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, JWTHandler.SECRET_KEY, algorithm=JWTHandler.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode(token: str) -> Dict[str, Any]:
        try:
            decoded_data = jwt.decode(token, JWTHandler.SECRET_KEY, algorithms=[JWTHandler.ALGORITHM])
            return decoded_data
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
