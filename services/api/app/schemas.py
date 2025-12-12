# from pydantic import BaseModel, EmailStr
# from typing import Optional

# class SignupRequest(BaseModel):
#     name: str
#     email: EmailStr
#     phone: Optional[str] = None
#     password: str

# class LoginRequest(BaseModel):
#     email: EmailStr
#     password: str

# class TokenResponse(BaseModel):
#     access_token: str
#     token_type: str = "bearer"


from pydantic import BaseModel
from typing import Optional

class SignupRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str
    role: str = "user"  # Add this

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: Optional[str] = None  # Add this
    user_id: Optional[int] = None  # Add this