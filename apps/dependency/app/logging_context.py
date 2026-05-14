from contextvars import ContextVar

correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="-")
trace_id_ctx: ContextVar[str] = ContextVar("trace_id", default="-")
