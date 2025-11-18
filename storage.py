import os
import shutil
from pathlib import Path
from typing import AsyncGenerator, Optional
from fastapi import UploadFile
from aiofiles import open as aio_open
from ..config import settings
from ..utils.file_validation import get_file_category, validate_file_type

class StorageService:
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_file(self, file: UploadFile, project_path: Path, filename: str) -> Path:
        """Save uploaded file to project directory"""
        dest_path = project_path / filename
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aio_open(dest_path, 'wb') as out_file:
            while content := await file.read(1024 * 1024):  # 1MB chunks
                await out_file.write(content)
        return dest_path
    
    async def save_chunk(self, chunk_data: bytes, project_path: Path, filename: str, chunk_index: int) -> Path:
        """Save a chunk for resumable upload"""
        chunks_dir = project_path / ".chunks" / filename
        chunks_dir.mkdir(parents=True, exist_ok=True)
        chunk_path = chunks_dir / f"chunk_{chunk_index:08d}"
        
        async with aio_open(chunk_path, 'wb') as out_file:
            await out_file.write(chunk_data)
        return chunk_path
    
    async def assemble_chunks(self, project_path: Path, filename: str, total_chunks: int) -> Path:
        """Assemble chunks into final file"""
        final_path = project_path / filename
        chunks_dir = project_path / ".chunks" / filename
        
        async with aio_open(final_path, 'wb') as final_file:
            for i in range(total_chunks):
                chunk_path = chunks_dir / f"chunk_{i:08d}"
                if not chunk_path.exists():
                    raise FileNotFoundError(f"Missing chunk {i}")
                async with aio_open(chunk_path, 'rb') as chunk_file:
                    while chunk := await chunk_file.read(1024 * 1024):
                        await final_file.write(chunk)
        
        # Clean up chunks
        shutil.rmtree(chunks_dir, ignore_errors=True)
        return final_path
    
    async def get_file_stream(self, file_path: Path) -> AsyncGenerator[bytes, None]:
        """Stream file for download"""
        async with aio_open(file_path, 'rb') as f:
            while chunk := await f.read(1024 * 1024):
                yield chunk
    
    def get_file_info(self, file_path: Path) -> dict:
        """Get file metadata"""
        return {
            "name": file_path.name,
            "size": file_path.stat().st_size,
            "modified": file_path.stat().st_mtime,
            "path": str(file_path.relative_to(self.upload_dir))
        }
    
    def get_project_files(self, project_path: Path) -> list:
        """Get all files in project directory (excluding .chunks)"""
        files = []
        for file_path in project_path.rglob("*"):
            if file_path.is_file() and ".chunks" not in str(file_path):
                files.append(self.get_file_info(file_path))
        return files
