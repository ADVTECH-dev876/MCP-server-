//(MCP JSON-RPC Layer)
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
import json
from typing import Any, Dict, List, Optional
from ..services.auth import get_current_user, require_project_permission
from ..services.projects import ProjectService
from ..services.upload import UploadService
from ..services.storage import StorageService
from ..models.user import User, Role
from ..models.project import Project
from ..config import settings

router = APIRouter()

# Initialize services
storage_service = StorageService()
upload_service = UploadService(storage_service)
project_service = ProjectService()

@router.post("/mcp")
async def mcp_endpoint(request: dict, current_user: User = Depends(get_current_user)):
    """MCP JSON-RPC endpoint"""
    try:
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "list_projects":
            result = await handle_list_projects(current_user, params)
        elif method == "get_project_files":
            result = await handle_get_project_files(current_user, params)
        elif method == "upload_file":
            result = await handle_upload_file(current_user, params)
        elif method == "initiate_resumable_upload":
            result = await handle_initiate_resumable_upload(current_user, params)
        elif method == "upload_chunk":
            result = await handle_upload_chunk(current_user, params)
        elif method == "finalize_upload":
            result = await handle_finalize_upload(current_user, params)
        elif method == "download_file":
            # Note: Downloads would be handled via separate endpoint for streaming
            raise HTTPException(status_code=400, detail="Use dedicated download endpoint")
        else:
            raise HTTPException(status_code=400, detail=f"Unknown method: {method}")
        
        return JSONResponse({
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        })
    
    except Exception as e:
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": str(e)},
            "id": request_id
        })

# Handler functions would implement the business logic
# Example:
async def handle_list_projects(user: User, params: dict):
    return await project_service.get_user_projects(user.id)

async def handle_get_project_files(user: User, params: dict):
    project_id = params.get("project_id")
    await require_project_permission(project_id, Role.VIEWER, user)
    project = await project_service.get_project(project_id)
    return storage_service.get_project_files(Path(settings.upload_dir) / project.storage_path)
