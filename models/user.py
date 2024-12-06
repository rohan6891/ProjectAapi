from pydantic import BaseModel
from typing import Optional

class RegisterReq(BaseModel):
    username: str
    password: str
    caseIds: Optional[dict[str, dict[str, str]]]

class User(BaseModel):
    username: str
    password: str
