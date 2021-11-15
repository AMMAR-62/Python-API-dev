from base64 import encode
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app import schemas
# SECRET KEY
# algorithm.
# the expiration time for the token.
SECRET_KEY = "69qDmADvfnjD5L4I1L6TTI9jdQ82T1CdgbDhnYn1rS2ik+/phTVysJ1gz3KUxqNwnaEdEoFVMACWqF861iuZPw=="
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# text - this key is encrypted from the aes encryption algorithm
# key - this is the secret key for the jwt token for api development course

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt= jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id: str = payload.get("users_id")
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id = id)
    except Exception as e:
        raise credentials_exception
