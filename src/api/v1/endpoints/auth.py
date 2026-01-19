from fastapi import APIRouter, Header, HTTPException, status, Depends
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import BaseModel
from src.core.config import settings

router = APIRouter()

class TokenRequest(BaseModel):
    tenant_id: str
    client_secret: str # In production, this would be a real API Key / Secret

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/token")
async def get_token(request: TokenRequest):
    """
    Endpoint to generate a Bearer Token for a tenant.
    In a real system, this would validate client_id/client_secret against a DB.
    """
    # Simplified validation: secret must match the one in config
    if request.client_secret != settings.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client secret"
        )
    
    access_token = create_access_token(data={"sub": request.tenant_id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/verify")
async def verify_token(
    authorization: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID")
):
    """
    Endpoint for Traefik's ForwardAuth middleware.
    Decodes the JWT and validates that the tenant matches.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header"
        )
    
    token = authorization.split(" ")[1]
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        tenant_from_token: str = payload.get("sub")
        if tenant_from_token is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        
        # Security check: Ensure the requested tenant matches the token's tenant
        if x_tenant_id and tenant_from_token != x_tenant_id:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token-Tenant mismatch")

        return {"status": "authenticated", "tenant_id": tenant_from_token}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
