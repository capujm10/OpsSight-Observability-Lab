from datetime import UTC, datetime
from threading import Lock

from app.models.order import Order, seed_orders
from app.schemas.order import OrderCreate
from app.telemetry.metrics import ORDERS_CREATED_TOTAL


class OrderService:
    def __init__(self) -> None:
        self._orders = seed_orders()
        self._lock = Lock()

    def list_orders(self) -> list[Order]:
        return list(self._orders.values())

    def get_order(self, order_id: int) -> Order | None:
        return self._orders.get(order_id)

    def create_order(self, payload: OrderCreate) -> Order:
        with self._lock:
            next_id = max(self._orders) + 1
            order = Order(next_id, payload.customer_id, payload.amount, "processing", datetime.now(UTC))
            self._orders[next_id] = order
            ORDERS_CREATED_TOTAL.inc()
            return order


order_service = OrderService()
