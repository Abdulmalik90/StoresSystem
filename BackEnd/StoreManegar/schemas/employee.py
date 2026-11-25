from pydantic import BaseModel, EmailStr, Field
from typing import Literal

class EmployeeCreate(BaseModel):
    ename: str = Field(..., min_length=2, max_length=75)
    google_sub: str | None = None
    email: EmailStr
    erole: Literal["admin", "cashier", "none"] = "none"
    mobile_number: str = Field(..., min_length=10, max_length=10)

class EmployeeUpdate(BaseModel):
    ename: str = Field(..., min_length=2, max_length=75)
    email: EmailStr
    erole: Literal["admin", "cashier", "none"] = "none"
    mobile_number   : str = Field(..., min_length=10, max_length=10)