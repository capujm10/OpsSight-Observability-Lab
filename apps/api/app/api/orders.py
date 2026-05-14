import logging
from dataclasses import asdict

from fastapi import APIRouter, HTTPException, status

from app.config.settings import get_settings
from app.log_context.context import get_correlation_id
from app.schemas.order import ApiResponse, OrderCreate, OrderResponse
from app.services.dependency import observed_dependency_call
from app.services.orders import order_service

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])
logger = logging.getLogger("opsight.orders")


@router.get("", response_model=ApiResponse)
async def list_orders() -> ApiResponse:
    await observed_dependency_call(get_settings(), operation="list-payment-state")
    orders = [OrderResponse(**asdict(order)) for order in order_service.list_orders()]
    return ApiResponse(status="success", data=orders, correlation_id=get_correlation_id())


@router.get("/{order_id}", response_model=ApiResponse)
async def get_order(order_id: int) -> ApiResponse:
    order = order_service.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order not found")
    logger.info("order retrieved", extra={"order_id": order_id})
    return ApiResponse(status="success", data=OrderResponse(**asdict(order)), correlation_id=get_correlation_id())


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate) -> ApiResponse:
    await observed_dependency_call(get_settings(), operation="authorize")
    order = order_service.create_order(payload)
    logger.info("order created", extra={"order_id": order.id})
    return ApiResponse(status="success", data=OrderResponse(**asdict(order)), correlation_id=get_correlation_id())
