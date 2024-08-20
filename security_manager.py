from asyncio import Lock
from datetime import datetime, timedelta
import jwt


class SecurityManager:
    _token: str

    def __init__(self, service_id: str, secret_key: str, lifetime: timedelta,
                 allowed_services: list[str] = []) -> None:
        self.secret_key = secret_key
        self.service_id = service_id
        self.liftetime = lifetime
        self.allowed_services = allowed_services
        
        self._lock = Lock()
        self._token = None
    
    async def generate_token(self):
        async with self._lock:
            self._token = jwt.encode({"service_id": self.service_id,
                                "exp": datetime.utcnow() + self.liftetime}, self.secret_key)
            return self._token

    async def use_token(self):
        if not self._token:
            return await self.generate_token()
        try:
            jwt.decode(self._token, self.secret_key, ["HS256"])
        except jwt.ExpiredSignatureError:
            return await self.generate_token()
        
        return self._token
    
    def process_token(self, token: str | bytes):
        try:
            _access = jwt.decode(token, self.secret_key, ["HS256"])
            if not (service_id := _access.get("service_id", None)):
                return False
            
            if "*" in self.allowed_services:
                return True
            if service_id in self.allowed_services:
                return True
            
            return False
            
        except jwt.InvalidTokenError:
            return False