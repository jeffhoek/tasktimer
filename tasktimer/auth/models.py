from typing import Optional
from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    user_id: str
    email: Optional[str] = None
