from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from models import User
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Annotated
from starlette import status

#Create router separated from main.py
authrouter = APIRouter(
    prefix='/auth',
    tags=['auth']
)

#Randomly generated secret for decoding JWT + HS256 Alg
SECRET_KEY = '8vai1z1cceq77k8e2y8s7dc90wjayjcfubmt8wcquefpv6eysg'
ALOGRITHM = 'HS256'
#Setup pass hashing and unhashing
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
#Create bearer on token endpoint of router file
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


#Auth function that matches user with db user and sees if hashed pass matches
def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

#Access token created with user, id and expire time encoded
def create_access_token(username: str, user_id:int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALOGRITHM) 

#Get current user by decoding the JWT token
async def get_current_user(token: Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALOGRITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'username': username, 'user_id': user_id}
    except JWTError: #Raised when decode fails
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    
user_dependency = Annotated[dict, Depends(get_current_user)]