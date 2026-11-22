from pydantic import BaseModel, Field

class CreateUpdate_Category(BaseModel):
    category_name: str = Field(..., min_length=2, max_length=30)
