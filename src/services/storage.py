import os
import shutil
import boto3
from abc import ABC, abstractmethod
from typing import Optional
from fastapi import UploadFile
from src.core.config import settings

class BaseStorage(ABC):
    @abstractmethod
    async def upload(self, file: UploadFile, tenant_id: str) -> str:
        """Uploads a file and returns the accessible URL or path."""
        pass

    @abstractmethod
    def get_path(self, identifier: str) -> str:
        """Returns the local path or URL for a given identifier."""
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

    def get_path(self, identifier: str) -> str:
        return identifier

class S3Storage(BaseStorage):
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        self.cloudfront_domain = settings.CLOUDFRONT_DOMAIN

    async def upload(self, file: UploadFile, tenant_id: str) -> str:
        s3_key = f"{tenant_id}/{file.filename}"
        
        # Upload to S3
        self.s3_client.upload_fileobj(
            file.file,
            self.bucket_name,
            s3_key,
            ExtraArgs={"ContentType": file.content_type}
        )
        
        # Return CloudFront URL if available, else S3 URL
        if self.cloudfront_domain:
            return f"https://{self.cloudfront_domain}/{s3_key}"
        
        return f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"

    def get_path(self, identifier: str) -> str:
        return identifier

def get_storage() -> BaseStorage:
    if settings.STORAGE_TYPE == "s3":
        return S3Storage()
    return LocalStorage()

storage = get_storage()
