from pydantic import BaseModel, EmailStr, Field

class EmployeeCreate(BaseModel):
    ename: str = Field(..., min_length=2, max_length=75)
    google_sub: str = Field(..., max_length=255, min_length=1)
    email: EmailStr
    erole: str = Field(..., min_length=2, max_length=50)
    mobile_number: str = Field(..., min_length=10, max_length=10)

class EmployeeUpdate(BaseModel):
    ename: str = Field(..., min_length=2, max_length=75)
    email: EmailStr
    erole: str = Field(..., min_length=2, max_length=50)
    mobile_number   : str = Field(..., min_length=10, max_length=10)