MCP Web Project Hosting Server
This implementation provides a robust, secure, and scalable MCP (Model Context Protocol) server for hosting web projects with large file upload support (up to 10GB), role-based access control, and efficient storage management.

Architecture Overview
Framework: FastAPI (async support, built-in validation, OpenAPI docs)
MCP Compatibility: Custom JSON-RPC layer over HTTP
Storage: Local filesystem with configurable path + optional integration points for cloud storage
Upload Strategy: Multipart for <1GB, resumable chunked for ≥1GB
Auth: JWT-based authentication with role-based permissions
Concurrency: Async I/O with proper backpressure handling
Key Features Implemented
1. Large File Upload Handling
Multipart uploads for files <1GB (standard FastAPI handling)
Resumable chunked uploads for files ≥1GB:
Initiation endpoint returns upload ID and chunk info
Chunk upload endpoints with progress tracking
Finalization endpoint assembles chunks
Streaming I/O: Files written directly to disk (never loaded fully into memory)
Chunk size: Configurable (default 10MB)
2. File Type & Size Validation
Category-based validation:
Images: ≤500MB
Videos: ≤2GB
Code: ≤100MB
Databases: ≤10GB
Extension and magic number validation
Customizable allowed types via config
3. Role-Based Access Control
Three-tier permission system:
Admin: Full access to all projects
Editor: Upload/delete/manage in assigned projects
Viewer: Read-only access
Project-specific permissions stored in DB
JWT authentication with 24h expiry
4. Efficient Storage Management
Hierarchical project storage (/uploads/{project_id}/...)
Chunk cleanup after successful assembly
File metadata tracking (size, modified time)
Storage usage monitoring (via file system stats)
5. MCP Compliance
JSON-RPC 2.0 compliant endpoints
Standard error responses
Method routing (list_projects, upload_file, etc.)
6. Security & Reliability
File type validation (extension + magic bytes)
Size limit enforcement
Authentication/authorization on all endpoints
Audit logging (setup in utils/logging.py)
Error handling for partial uploads/storage failures
7. Performance Optimizations
Async I/O throughout (FastAPI + SQLAlchemy async)
Streaming responses for downloads
Chunked processing to avoid memory exhaustion
Concurrent upload support (multiple users/projects)
Deployment Considerations
Production Security:
Set strong SECRET_KEY
Restrict CORS origins
Use HTTPS
Implement rate limiting
Storage Scaling:
Replace local storage with cloud backend (S3/Azure) by modifying StorageService
Add storage quota enforcement per project/user
Monitoring:
Add Prometheus metrics for uploads/downloads
Set up log aggregation (ELK stack)
Monitor disk space usage
Backup Strategy:
Regular backups of database + upload directory
Consider versioning for critical files
High Availability:
Deploy with multiple workers (uvicorn --workers 4)
Use load balancer for multi-instance setup
Shared storage for uploads (NFS/cloud)
This implementation provides a robust foundation that meets all specified requirements while maintaining extensibility for future enhancements.

