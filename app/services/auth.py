from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")
ALGORITHM = "HS256"

def verify_token(token : str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("user") != "nodejs-server":
            raise HTTPException(status_code=403, detail=f"Invalid token")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token verification failed: {str(e)}")

def get_info(token : str = Depends(oauth2_scheme)):
    return verify_token(token)