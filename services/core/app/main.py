from fastapi import FastAPI

from app import health
from app.config import get_settings
from app.logging_config import configure_logging
from app.routers import items, orders

configure_logging(get_settings().log_level)

app = FastAPI(title="Core Service")
app.include_router(health.router)
app.include_router(items.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
