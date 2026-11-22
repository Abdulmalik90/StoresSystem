from pydantic import BaseModel, EmailStr, Field

class CreateUpdate_Supplier(BaseModel):
    sname: str = Field(..., min_length=2, max_length=75)
    mobile_number: str = Field(..., min_length=10, max_length=10)
    email: EmailStr
