from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials
from core.guards.guard import Guard
from plugins.microservices.security_manager import SecurityManager
from settings import AUTHORIZATION_SCHEME


class InternalEndpoint(Guard):
    def __init__(self, error_code: int = 404,
                 error_msg: str = "Endpoint not found") -> None:
        self.error_code = error_code
        self.error_msg = error_msg
    
    async def handle_access(self, 
                            token: HTTPAuthorizationCredentials = Security(AUTHORIZATION_SCHEME)):
        security_manager = self.service_registry.get_singletone(SecurityManager)

        if not security_manager:
            raise HTTPException(403, "Internal requests aren't allowed & enabled")
        
        if not security_manager.process_token(token.credentials):
            raise HTTPException(self.error_code, self.error_msg)