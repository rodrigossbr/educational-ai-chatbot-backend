from django.core.cache import cache

class SessionContextService:
    _KEY = "ctx:{id}"
    _TTL = 60 * 30  # 30 min

    def get(self, session_id: int) -> dict:
        return cache.get(self._KEY.format(id=session_id), {}) or {}

    def update(self, session_id: int, **kwargs) -> dict:
        ctx = self.get(session_id)
        for k, v in kwargs.items():
            if v not in (None, ""):
                ctx[k] = v
        cache.set(self._KEY.format(id=session_id), ctx, self._TTL)
        return ctx

    def clear(self, session_id: int):
        cache.delete(self._KEY.format(id=session_id))
