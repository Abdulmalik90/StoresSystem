from pydantic import BaseModel, Field

class CreateUpdate_Customer(BaseModel):
    cname: str = Field(..., min_length=2, max_length=75)
    mobile_number: str = Field(..., min_length=10, max_length=10)

