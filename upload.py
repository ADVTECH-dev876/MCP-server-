import os
import hashlib
from pathlib import Path
from typing import Optional
from fastapi import HTTPException, status
from ..config import settings
from ..utils.file_validation import get_file_category, validate_file_type

class UploadService:
    def __init__(self, storage_service):
        self.storage = storage_service
    
    async def handle_upload(self, file: UploadFile, project_path: Path, user_id: int) -> dict:
        """Handle regular file upload (<1GB)"""
        # Validate file
        validation_result = validate_file_type(file.filename, await file.read(1024))
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {validation_result['error']}"
            )
        
        # Reset file pointer after reading for validation
        await file.seek(0)
        
        # Check size limits
        category = validation_result["category"]
        if file.size > settings.max_sizes.get(category, settings.max_file_size):
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large for {category} category"
            )
        
        # Save file
        saved_path = await self.storage.save_file(file, project_path, file.filename)
        
        return {
            "filename": file.filename,
            "size": file.size,
            "path": str(saved_path.relative_to(settings.upload_dir)),
            "category": category
        }
    
    def initiate_resumable_upload(self, filename: str, file_size: int, project_path: Path) -> dict:
        """Initiate resumable upload session"""
        # Validate file type first
        validation_result = validate_file_type(filename, b"")
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {validation_result['error']}"
            )
        
        category = validation_result["category"]
        if file_size > settings.max_sizes.get(category, settings.max_file_size):
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large for {category} category"
            )
        
        # Generate upload ID
        upload_id = hashlib.md5(f"{filename}{file_size}{project_path}".encode()).hexdigest()
        
        return {
            "upload_id": upload_id,
            "chunk_size": settings.chunk_size,
            "total_chunks": (file_size + settings.chunk_size - 1) // settings.chunk_size,
            "category": category
        }
    
    async def upload_chunk(self, upload_id: str, chunk_index: int, chunk_data: bytes, 
                          filename: str, project_path: Path) -> dict:
        """Upload a single chunk"""
        saved_path = await self.storage.save_chunk(chunk_data, project_path, filename, chunk_index)
        return {"chunk_index": chunk_index, "status": "uploaded"}
    
    async def finalize_upload(self, upload_id: str, filename: str, total_chunks: int, 
                            project_path: Path) -> dict:
        """Finalize resumable upload and assemble file"""
        final_path = await self.storage.assemble_chunks(project_path, filename, total_chunks)
        return {
            "filename": filename,
            "size": final_path.stat().st_size,
            "path": str(final_path.relative_to(settings.upload_dir))
        }
