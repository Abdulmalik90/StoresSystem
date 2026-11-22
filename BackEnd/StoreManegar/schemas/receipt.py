from pydantic import BaseModel, Field

class ReceiptItemCreate(BaseModel):
    pid: str = Field(..., max_length=36, min_length=36)
    quantity: int = Field(..., gt=0)

class ReceiptCreate(BaseModel):
    cid: str = Field(..., max_length=36, min_length=36)
    eid: str = Field(..., max_length=36, min_length=36)
    items: list[ReceiptItemCreate] = Field(..., min_length=1)

class ReceiptUpdate(BaseModel):
    cid: str = Field(..., min_length=36, max_length=36)
    eid: str = Field(..., min_length=36, max_length=36)

