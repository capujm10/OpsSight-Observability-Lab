from datetime import datetime

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    customer_id: str = Field(min_length=3, examples=["cust-enterprise-001"])
    amount: float = Field(gt=0, examples=[499.0])


class OrderResponse(BaseModel):
    id: int
    customer_id: str
    amount: float
    status: str
    created_at: datetime


class ApiResponse(BaseModel):
    status: str
    data: object
    correlation_id: str
