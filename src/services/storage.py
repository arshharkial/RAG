import os
import shutil
from abc import ABC, abstractmethod
from fastapi import UploadFile
from src.core.config import settings

class BaseStorage(ABC):
    @abstractmethod
    async def upload(self, file: UploadFile, tenant_id: str) -> str:
        pass

    @abstractmethod
    def get_path(self, file_path: str) -> str:
        pass

class LocalStorage(BaseStorage):
    def __init__(self, base_dir: str = "storage"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    async def upload(self, file: UploadFile, tenant_id: str) -> str:
        tenant_dir = os.path.join(self.base_dir, tenant_id)
        os.makedirs(tenant_dir, exist_ok=True)
        
        file_path = os.path.join(tenant_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return file_path

    def get_path(self, file_path: str) -> str:
        return file_path

storage = LocalStorage()
