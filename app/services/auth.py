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
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_info(token : str = Depends(oauth2_scheme)):
    return verify_token(token)