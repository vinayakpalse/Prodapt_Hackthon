from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DocumentPublic(BaseModel):
    id: str
    title: str
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(from_attributes=True)
