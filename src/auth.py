import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from rewire import config

from src.models import User


@config
class Config(BaseModel):
    jwt_secret: str
    jwt_algorithm: str


def generate_access_token(user_id: int) -> str:
    return jwt.encode(
        {'user_id': user_id},
        Config.jwt_secret,
        Config.jwt_algorithm
    )


async def user_required(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> User:
    try:
        payload = jwt.decode(credentials.credentials, Config.jwt_secret, algorithms=[Config.jwt_algorithm])
    except Exception:
        raise HTTPException(401, 'Invalid token!')

    user = await User.get_by_id(payload.get('user_id'))
    if not user:
        raise HTTPException(401, 'Unknown user!')

    return user


async def admin_required(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> User:
    user = await user_required(credentials)
    if not user.is_admin:
        raise HTTPException(403, 'Admin privileges required!')

    return user
