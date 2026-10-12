import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

logger = logging.getLogger("api.request")

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to intercept incoming requests and outgoing responses,
    logging process times, latencies, status codes, and exceptions.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            # Skip noisy health checks unless degraded
            if request.url.path == "/health" and response.status_code == 200:
                return response

            logger.info(
                "Request completed",
                extra={
                    "method": request.method,
                    "url": str(request.url.path),
                    "status_code": response.status_code,
                    "latency_ms": round(process_time, 2)
                }
            )
            return response
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                "Request failed with unhandled exception",
                exc_info=True,
                extra={
                    "method": request.method,
                    "url": str(request.url.path),
                    "latency_ms": round(process_time, 2),
                    "error": str(e)
                }
            )
            raise
