from os import access
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter


from app import models, schemas, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
# from ..utils import hash
router = APIRouter(prefix="/auth",tags=['Autentication'])

@router.post('/login')
def login(user_credentials: schemas.UserLogin, db: Session= Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    print(user, end="\n\n\n\n\n")
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credential")
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credential")
    
    access_token = oauth2.create_access_token(data = {"user_id": user.id})

    #create a token
    # return token
    return {"access_token" : access_token, "token_type": "bearer"}

