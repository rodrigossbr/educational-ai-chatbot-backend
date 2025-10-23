import time
import httpx
from typing import Dict, Any, Optional

class HttpClientService:
    def __init__(self, base_url: str, timeout: float = 6.0, retries: int = 3):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self._client = httpx.Client(base_url=self.base_url, timeout=self.timeout)

    def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        last_exc = None
        for attempt in range(1, self.retries + 1):
            try:
                return self._client.request(method, url, **kwargs)
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError) as exc:
                last_exc = exc
                time.sleep(0.2 * (2 ** (attempt - 1)))
        raise last_exc

    def get(self, path: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None):
        return self._request("GET", path, params=params, headers=headers)

    def post(self, path: str, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None):
        return self._request("POST", path, json=json, headers=headers)
