from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime
from bson import ObjectId


class Post(BaseModel):
    post_link: str
    images: Optional[List[dict]]  # {"image_url": str}
    created_at: datetime

class Tweet(BaseModel):
    tweet: str
    date: datetime
    img_link: Optional[str]

class ChatMessage(BaseModel):
    sender: str
    message: str
    timestamp: datetime

class Chat(BaseModel):
    receiver_name: str
    messages: List[ChatMessage]

class Follower(BaseModel):
    profile_id: str
    profile_link: str

class Following(BaseModel):
    profile_id: str
    profile_link: str

class InstagramData(BaseModel):
    platform_type: str = "Instagram"
    last_updated: datetime
    username: str
    posts: List[Post]
    chats: Optional[List[Chat]] = []
    followers: List[Follower]
    following: List[Following]

class TwitterData(BaseModel):
    platform_type: str = "Twitter"
    last_updated: datetime
    username: str
    tweets: List[Tweet]
    chats: Optional[List[Chat]] = []
    followers: List[Follower]
    following: List[Following]

class DataEntry(BaseModel):
    data: List[Union[InstagramData, TwitterData]]
