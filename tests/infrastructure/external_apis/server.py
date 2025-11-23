"""
Mock HTTP Server for External APIs.

This module provides a FastAPI-based mock server that serves API responses
based on OpenAPI specifications and payload files. The server can be started
programmatically for testing purposes.
"""
from __future__ import annotations

import json
import re
import socket
from pathlib import Path
from typing import Any, Dict, Optional, List
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from threading import Thread
import time

from .posts.spec_loader import OpenAPISpecLoader


class MockAPIServer:
    """
    Mock HTTP server for external APIs based on OpenAPI specifications.
    
    The server dynamically creates routes from OpenAPI specs and serves
    responses from payload files mapped via x-mock-payload extensions.
    """
    
    def __init__(self, api_name: str, spec_path: Path, port: int = 0):
        """
        Initialize mock API server.
        
        Args:
            api_name: Name of the API (e.g., "posts", "payments")
            spec_path: Path to OpenAPI YAML specification file
            port: Port to run server on (0 = random available port)
        """
        self.api_name = api_name
        self.spec_path = spec_path
        self.port = port
        self.app = FastAPI(title=f"Mock {api_name.title()} API")
        self.spec_loader = OpenAPISpecLoader(spec_path)
        self.spec_dir = spec_path.parent
        self._server_thread: Optional[Thread] = None
        self._server_process: Optional[uvicorn.Server] = None
        self._actual_port: Optional[int] = None
        self._state: Dict[str, Any] = {}  # For maintaining state (e.g., deleted resources)
        
        # Load spec and build routes
        self._build_routes()
    
    def _load_json_file(self, file_path: Path) -> Any:
        """Load JSON file from path."""
        if not file_path.exists():
            raise FileNotFoundError(f"Payload file not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _resolve_path_params(self, path_template: str, actual_path: str) -> Dict[str, str]:
        """
        Extract path parameters from actual path using template.
        
        Example:
            template: "/posts/{id}"
            actual: "/posts/123"
            returns: {"id": "123"}
        """
        params = {}
        template_parts = path_template.split("/")
        actual_parts = actual_path.split("/")
        
        if len(template_parts) != len(actual_parts):
            return params
        
        for template_part, actual_part in zip(template_parts, actual_parts):
            if template_part.startswith("{") and template_part.endswith("}"):
                param_name = template_part[1:-1]
                params[param_name] = actual_part
        
        return params
    
    def _find_matching_payload(
        self, 
        method: str, 
        path: str, 
        status_code: str = "200",
        path_params: Optional[Dict[str, str]] = None
    ) -> Optional[Any]:
        """
        Find payload file for a given endpoint.
        
        Tries multiple strategies:
        1. Exact match with path params (e.g., GET_posts_999_200.json for id=999)
        2. Template match only if ID matches (e.g., GET_posts_1_200.json for id=1)
        3. Generic match only if no ID parameter (e.g., GET_posts_200.json)
        """
        path_params = path_params or {}
        spec = self.spec_loader._load_spec()
        
        # Find matching path in spec
        for spec_path, path_item in spec.get("paths", {}).items():
            # Check if this spec path matches the actual path
            if not self._path_matches(spec_path, path):
                continue
            
            # Extract path params
            extracted_params = self._resolve_path_params(spec_path, path)
            path_params.update(extracted_params)
            
            # Check if method exists
            operation = path_item.get(method.lower())
            if not operation:
                continue
            
            # Get response
            responses = operation.get("responses", {})
            response = responses.get(status_code)
            if not response:
                continue
            
            # Get payload path from x-mock-payload
            mock_payload = response.get("x-mock-payload")
            if not mock_payload:
                continue
            
            payload_path_template = self.spec_dir / mock_payload
            
            # If we have an ID parameter, we need exact match or matching ID in filename
            if path_params and "id" in path_params:
                requested_id = path_params["id"]
                
                # Strategy 1: Try exact match with ID (e.g., GET_posts_999_200.json)
                try:
                    payload_path = Path(str(payload_path_template).format(**path_params))
                    if payload_path.exists():
                        return self._load_json_file(payload_path)
                except (KeyError, ValueError):
                    pass
                
                # Strategy 2: Check if template file has matching ID
                # For specific IDs, we must have an exact match or matching ID in filename
                if not payload_path_template.exists():
                    # Template file doesn't exist, skip this response
                    continue
                
                template_name = Path(payload_path_template).stem
                import re as re_module
                # Extract all numbers from filename
                numbers = re_module.findall(r'(\d+)', template_name)
                
                # Check if any number (except status code at end) matches requested ID
                id_matched = False
                if numbers and len(numbers) > 1:
                    # Check all numbers except the last one (status code)
                    for num_str in numbers[:-1]:
                        if num_str == requested_id:
                            # ID matches! Use this payload
                            payload = self._load_json_file(payload_path_template)
                            if isinstance(payload, dict):
                                payload = payload.copy()
                                payload["id"] = int(requested_id)
                            return payload
                    # Template has a different ID, don't use it
                    id_matched = False
                elif len(numbers) == 1:
                    # Only one number - could be status code or ID
                    # If it matches requested ID, use it
                    if numbers[0] == requested_id:
                        payload = self._load_json_file(payload_path_template)
                        if isinstance(payload, dict):
                            payload = payload.copy()
                            payload["id"] = int(requested_id)
                        return payload
                    # Otherwise, it's probably status code, don't use it
                    id_matched = False
                else:
                    # No numbers in filename - generic template, don't use for specific IDs
                    id_matched = False
                
                # If we have an ID but template doesn't match, skip this response
                if not id_matched:
                    continue
            else:
                # No ID parameter - use template as-is (for endpoints like GET /posts)
                if payload_path_template.exists():
                    return self._load_json_file(payload_path_template)
        
        return None
    
    def _path_matches(self, template: str, actual: str) -> bool:
        """
        Check if actual path matches template path.
        
        Example:
            template: "/posts/{id}"
            actual: "/posts/123"
            returns: True
        """
        # Convert template to regex
        pattern = re.sub(r"\{[^}]+\}", r"[^/]+", template)
        pattern = f"^{pattern}$"
        return bool(re.match(pattern, actual))
    
    def _build_routes(self):
        """Build FastAPI routes from OpenAPI specification."""
        spec = self.spec_loader._load_spec()
        
        for path, path_item in spec.get("paths", {}).items():
            # Register each HTTP method
            for method in ["get", "post", "put", "delete", "patch"]:
                operation = path_item.get(method)
                if not operation:
                    continue
                
                # Create route handler factory to capture variables correctly
                def make_handler(method_name: str, spec_path: str, operation_def: Dict[str, Any]):
                    async def route_handler(request: Request):
                        return await self._handle_request(request, method_name, spec_path, operation_def)
                    return route_handler
                
                # Create handler with captured variables
                route_handler = make_handler(method, path, operation)
                
                # Register route with FastAPI
                route_path = path
                # FastAPI uses {param} format, which matches OpenAPI
                
                if method == "get":
                    self.app.get(route_path)(route_handler)
                elif method == "post":
                    self.app.post(route_path)(route_handler)
                elif method == "put":
                    self.app.put(route_path)(route_handler)
                elif method == "delete":
                    self.app.delete(route_path)(route_handler)
                elif method == "patch":
                    self.app.patch(route_path)(route_handler)
    
    async def _handle_request(
        self, 
        request: Request, 
        method: str, 
        spec_path: str,
        operation: Dict[str, Any]
    ) -> Response:
        """
        Handle incoming HTTP request and return appropriate response.
        
        Args:
            request: FastAPI request object
            method: HTTP method
            spec_path: Path template from OpenAPI spec
            operation: Operation definition from OpenAPI spec
            
        Returns:
            FastAPI Response with payload or error
        """
        actual_path = request.url.path
        path_params = self._resolve_path_params(spec_path, actual_path)
        
        # Check for state-based responses (e.g., deleted resources)
        if method.lower() == "get" and "id" in path_params:
            resource_id = path_params.get("id")
            deleted_key = f"deleted_{self.api_name}_{resource_id}"
            if self._state.get(deleted_key):
                # Return 404 for deleted resource
                payload = self._find_matching_payload(method, actual_path, "404", path_params)
                if payload:
                    return JSONResponse(content=payload, status_code=404)
        
        # Handle DELETE - update state and return 204
        if method.lower() == "delete":
            if "id" in path_params:
                resource_id = path_params.get("id")
                deleted_key = f"deleted_{self.api_name}_{resource_id}"
                # Check if resource exists (not deleted)
                payload = self._find_matching_payload("get", actual_path, "200", path_params)
                if payload is None:
                    # Resource doesn't exist
                    error_payload = self._find_matching_payload("get", actual_path, "404", path_params)
                    if error_payload:
                        return JSONResponse(content=error_payload, status_code=404)
                    return JSONResponse(
                        content={"error": "Not found", "message": f"Resource not found"},
                        status_code=404
                    )
                # Mark as deleted and return 204
                self._state[deleted_key] = True
                return Response(status_code=204)
            else:
                # DELETE without ID - return 204
                return Response(status_code=204)
        
        # Determine status code based on method and operation
        default_status = {
            "get": "200",
            "post": "201",
            "put": "200",
            "patch": "200"
        }.get(method.lower(), "200")
        
        # Try to find payload
        payload = self._find_matching_payload(method, actual_path, default_status, path_params)
        
        if payload is None:
            # Try 404
            payload = self._find_matching_payload(method, actual_path, "404", path_params)
            if payload:
                return JSONResponse(content=payload, status_code=404)
            # No payload found
            return JSONResponse(
                content={"error": "Not found", "message": f"No mock payload found for {method} {actual_path}"},
                status_code=404
            )
        
        # Handle POST/PUT - merge request body if needed
        if method.lower() in ["post", "put"] and request.method in ["POST", "PUT"]:
            try:
                request_body = await request.json()
                if isinstance(payload, dict):
                    payload = payload.copy()
                    payload.update(request_body)
                    # Update ID if in path params
                    if "id" in path_params:
                        try:
                            payload["id"] = int(path_params["id"])
                        except ValueError:
                            pass
            except Exception:
                pass  # Use payload as-is if body parsing fails
        
        # Return response
        status_code = int(default_status)
        if method.lower() == "post":
            status_code = 201
        elif method.lower() == "delete":
            status_code = 204
        
        if status_code == 204:
            return Response(status_code=204)
        
        return JSONResponse(content=payload, status_code=status_code)
    
    def _find_free_port(self) -> int:
        """Find a free port on the system."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def start(self) -> int:
        """
        Start the mock server in a background thread.
        
        Returns:
            Port number the server is running on
        """
        if self._server_thread and self._server_thread.is_alive():
            return self._actual_port or self.port
        
        # If port is 0, find a free port
        if self.port == 0:
            self.port = self._find_free_port()
            self._actual_port = self.port
        
        config = uvicorn.Config(
            app=self.app,
            host="127.0.0.1",
            port=self.port,
            log_level="error"  # Suppress uvicorn logs during tests
        )
        self._server_process = uvicorn.Server(config)
        
        def run_server():
            self._server_process.run()
        
        self._server_thread = Thread(target=run_server, daemon=True)
        self._server_thread.start()
        
        # Wait for server to start - verify it's listening on the port
        max_attempts = 50
        for attempt in range(max_attempts):
            try:
                # Try to connect to verify server is up
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('127.0.0.1', self.port))
                sock.close()
                if result == 0:
                    # Server is listening
                    self._actual_port = self.port
                    return self._actual_port
            except Exception:
                pass
            
            time.sleep(0.1)
        
        raise RuntimeError(f"Failed to start mock server on port {self.port}")
    
    def stop(self):
        """Stop the mock server."""
        if self._server_process:
            self._server_process.should_exit = True
        if self._server_thread:
            self._server_thread.join(timeout=2.0)
        self._state.clear()
    
    def get_base_url(self) -> str:
        """
        Get base URL of the running server.
        
        Returns:
            Base URL (e.g., "http://127.0.0.1:8000")
        """
        port = self._actual_port or self.port
        if port == 0:
            raise RuntimeError("Server not started yet. Call start() first.")
        return f"http://127.0.0.1:{port}"
    
    def reset_state(self):
        """Reset server state (e.g., clear deleted resources)."""
        self._state.clear()

