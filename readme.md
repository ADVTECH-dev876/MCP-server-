MCP Web Project Hosting Server
This implementation provides a robust, secure, and scalable MCP (Model Context Protocol) server for hosting web projects with large file upload support (up to 10GB), role-based access control, and efficient storage management.

Architecture Overview
Framework: FastAPI (async support, built-in validation, OpenAPI docs)
MCP Compatibility: Custom JSON-RPC layer over HTTP
Storage: Local filesystem with configurable path + optional integration points for cloud storage
Upload Strategy: Multipart for <1GB, resumable chunked for ≥1GB
Auth: JWT-based authentication with role-based permissions
Concurrency: Async I/O with proper backpressure handling
