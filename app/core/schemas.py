from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from fastapi import UploadFile



class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    avatar: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    avatar: Optional[UploadFile] = None
    banner: Optional[UploadFile] = None


class DefaultResponse(BaseModel):
    State: int
    Message: str

class ActivationStatusResponse(BaseModel):
    email: str
    is_activated: bool

class Token(BaseModel):
    access_token: str
    user_id: int

class UserResponse(BaseModel):
    id: int
    username: str
    tag: str
    description: Optional[str]
    address: Optional[str]
    created_at: datetime
    avatar: Optional[str]
    banner: Optional[str]

    class Config:
        from_attributes = True
    
class UserWithFollowStatus(BaseModel):
    id: int
    username: str
    tag: str
    avatar: Optional[str]
    is_following: bool

class UsersResponse2(BaseModel):
    users: list[UserWithFollowStatus]
    is_authenticated: bool




class AuthorResponse(BaseModel):
    id: int
    username: Optional[str]
    tag: str
    avatar: Optional[str]

class PostResponse(BaseModel):
    id: int
    text: str
    author: AuthorResponse
    created_at: datetime
    parent_id: Optional[int]
    likes_count: int
    comments_count: int
    is_liked: bool
    is_authenticated: bool

class PostCreate(BaseModel):
    text: str
    parent_id: Optional[int] = None




class LikeToggleResponse(BaseModel):
    liked: bool




class Follow(BaseModel):
    follower_id: int
    followed_id: int
    created_at: datetime

    class Config:
        from_attributes = True

