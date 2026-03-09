from fastapi import Request
import httpx

def get_ai_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.ai_http_client

def get_payments_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.payments_http_client