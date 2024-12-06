from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class ObjectIdStr(str):
    def _new_(cls, value):
        if isinstance(value, ObjectId):
            value = str(value)
        return str._new_(cls, value)
    
class Case(BaseModel):
    case_number: str
    title: str
    description: Optional[str]
    suspect_name: Optional[List[str]] = []
    linked_data: Optional[List[dict]] = []
    ml_analysis: Optional[dict] = None
    report: Optional[dict] = None
    status: str
    user_id: ObjectIdStr
    created_at: datetime
    updated_at: datetime

    class Config:
        # This tells Pydantic to allow ObjectId to be used as a valid type
        json_encoders = {
            ObjectId: str
        }
        arbitrary_types_allowed = True
