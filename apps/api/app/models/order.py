from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(slots=True)
class Order:
    id: int
    customer_id: str
    amount: float
    status: str
    created_at: datetime


def seed_orders() -> dict[int, Order]:
    now = datetime.now(UTC)
    return {
        1001: Order(1001, "cust-enterprise-001", 1299.0, "paid", now),
        1002: Order(1002, "cust-growth-044", 249.0, "processing", now),
        1003: Order(1003, "cust-platform-019", 899.0, "paid", now),
    }
