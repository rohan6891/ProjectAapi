from pydantic import BaseModel
from typing import Dict, Optional

# Models
class RegisterReq(BaseModel):
    username: str
    password: str
    caseIds: Optional[Dict[str, Dict[str, str]]] = None

class LoginReq(BaseModel):
    username: str
    password: str
