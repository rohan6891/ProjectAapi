from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class Image(BaseModel):
    image_url: str

class Post(BaseModel):
    post_link: str
    images: List[Image]
    created_at: datetime

class Message(BaseModel):
    sender: Optional[str] = None
    message: Optional[str] = None
    timestamp: Optional[datetime] = None

class Chat(BaseModel):
    receiver_name: str
    messages: Optional[List[Message]] = []

class Follower(BaseModel):
    profile_id: Optional[str] = None
    profile_link: str

class Following(BaseModel):
    profile_id: Optional[str] = None
    profile_link: str

class Tweet(BaseModel):
    date: datetime
    time: str
    tweet: Optional[str] = None
    img_link: Optional[str] = None

class DataEntry(BaseModel):
    _id: ObjectId
    user_id: ObjectId
    platform_type: str
    last_updated: datetime
    username: str
    posts: Optional[List[Post]] = []
    tweets: Optional[List[Tweet]] = []
    chats: Optional[List[Chat]] = []
    followers: List[Follower]
    following: List[Following]
    
    class Config:
        arbitrary_types_allowed = True

class InputModel(BaseModel):
    _id: ObjectId
    data: List[DataEntry]

    class Config:
        arbitrary_types_allowed = True
