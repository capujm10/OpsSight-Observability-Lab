from contextvars import ContextVar

correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="-")
trace_id_ctx: ContextVar[str] = ContextVar("trace_id", default="-")


def get_correlation_id() -> str:
    return correlation_id_ctx.get()


def set_correlation_id(value: str) -> None:
    correlation_id_ctx.set(value)


def set_trace_id(value: str) -> None:
    trace_id_ctx.set(value)
