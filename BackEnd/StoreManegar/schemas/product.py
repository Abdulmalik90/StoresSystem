from pydantic import BaseModel, Field

class CreateUpdate_Product(BaseModel):
    pname: str = Field(..., min_length=2, max_length=75)
    price: float = Field(..., gt=0, lt=100000000)
    quantity: int = Field(..., ge=0)
    discount: float = Field(default=0.0, ge=0, lt=100000000)
    sid: str = Field(..., min_length=36, max_length=36)
    category_id: str = Field(..., min_length=36, max_length=36)