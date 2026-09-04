from .exchange import router as exchange_router
from .news import router as news_router
from .prediction import router as prediction_router
from .alerts import router as alerts_router

__all__ = ["exchange_router", "news_router", "prediction_router", "alerts_router"]
