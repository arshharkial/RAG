from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Text
from src.core.database import Base, AsyncSessionLocal

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False)  # e.g., "query", "ingest", "delete"
    resource_id = Column(String, nullable=True)
    actor_id = Column(String, nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLogger:
    @staticmethod
    async def log(
        tenant_id: str, 
        action: str, 
        resource_id: str = None, 
        actor_id: str = None, 
        payload: dict = None
    ):
        import uuid
        async with AsyncSessionLocal() as session:
            new_log = AuditLog(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                action=action,
                resource_id=resource_id,
                actor_id=actor_id,
                payload=payload
            )
            session.add(new_log)
            await session.commit()

audit_logger = AuditLogger()
