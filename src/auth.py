import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from hashids import Hashids
from pydantic import BaseModel
from rewire import config

from src.models import User


@config
class Config(BaseModel):
    secret: str
    algorithm: str


def encode_user_id(user_id: int) -> str:
    encoder = Hashids(salt=Config.secret)
    return encoder.encode(user_id)


def decode_user_id(encoded_value: str) -> int:
    decoder = Hashids(salt=Config.secret)
    return decoder.decode(encoded_value)[0]


def generate_access_token(user_id: int) -> str:
    return jwt.encode(
        {'user_id': user_id},
        Config.secret,
        Config.algorithm
    )


async def user_required(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> User:
    try:
        payload = jwt.decode(credentials.credentials, Config.secret, algorithms=[Config.algorithm])
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


async def owner_required(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> User:
    user = await user_required(credentials)
    if not user.is_owner:
        raise HTTPException(403, 'Owner privileges required!')

    return user
