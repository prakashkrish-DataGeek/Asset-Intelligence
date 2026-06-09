"""
Asset Intelligence Copilot — MCP Protocol Definitions
=====================================================
Defines the JSON-RPC 2.0 inspired message shapes used by the local MCP server.
This module establishes the contract boundary between the agent and enterprise tools,
aligned with the Model Context Protocol semantics.

Architectural intent:
- The protocol is transport-agnostic. Today it runs in-process; tomorrow it could be
  HTTP/SSE or stdio without changing these definitions.
- Every message carries a requestId for distributed tracing.
- Tool and Resource definitions are self-describing so agents can discover capabilities
  dynamically rather than hard-coding tool names.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class MCPMethod(str, Enum):
    """Canonical MCP methods supported by this server."""
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    INITIALIZE = "initialize"


@dataclass
class ToolDefinition:
    """Self-describing tool schema for dynamic discovery."""
    name: str
    description: str
    input_schema: Dict[str, Any]  # JSON Schema subset
    output_shape: Dict[str, Any]  # Human-readable description of returned structure


@dataclass
class ResourceDefinition:
    """Self-describing resource for dynamic discovery."""
    uri: str
    name: str
    description: str
    mime_type: str = "text/plain"


@dataclass
class MCPRequest:
    """JSON-RPC style request envelope."""
    jsonrpc: str = "2.0"
    id: str = "0"
    method: str = ""
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPResponse:
    """JSON-RPC style response envelope."""
    jsonrpc: str = "2.0"
    id: str = "0"
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

    def is_error(self) -> bool:
        return self.error is not None


@dataclass
class ToolCallResult:
    """Structured result of a tool invocation, designed for evidence tracing."""
    tool_name: str
    arguments: Dict[str, Any]
    status: str  # "success" | "error"
    data: Any
    execution_time_ms: Optional[float] = None
    data_lineage: Dict[str, Any] = field(default_factory=dict)
