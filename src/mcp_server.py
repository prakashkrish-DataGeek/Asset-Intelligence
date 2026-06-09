"""
Asset Intelligence Copilot — Lightweight Local MCP Server
===========================================================
Implements an in-process MCP server abstraction that exposes enterprise data
through standardized Tools and Resources. This demonstrates how a CAIO would
insert a protocol boundary between AI agents and operational systems without
requiring immediate cloud migration or API rewrites.

Design choices:
- In-process today, but the request/response shapes mirror real JSON-RPC over SSE.
- SQLite and filesystem are the "enterprise systems" in this pilot.
- Every tool call returns structured, traceable data with lineage metadata.
"""

import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import config
from mcp_protocol import (
    MCPMethod,
    MCPRequest,
    MCPResponse,
    ToolDefinition,
    ResourceDefinition,
    ToolCallResult,
)


class AssetIntelligenceMCPServer:
    """
    Local MCP server exposing operational data as Tools and Resources.

    In a production deployment, this boundary would be hosted as a separate
    microservice (Python/FastAPI or Node/MCP SDK) with authentication,
    rate limiting, and audit logging. Here, we keep it in-process for
    demo portability while preserving the protocol semantics.
    """

    def __init__(self, db_path: Path, sharepoint_dir: Path):
        self.db_path = db_path
        self.sharepoint_dir = sharepoint_dir
        self._tools: List[ToolDefinition] = self._define_tools()
        self._resources: List[ResourceDefinition] = self._define_resources()

    # ------------------------------------------------------------------
    # Tool & Resource Definitions
    # ------------------------------------------------------------------

    def _define_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(
                name="query_modern_telemetry",
                description="Query the last N hours of structured telemetry (pressure, temperature, status) for a given asset from the operational historian (SQLite).",
                input_schema={
                    "type": "object",
                    "properties": {
                        "asset_id": {"type": "string", "description": "Asset identifier, e.g., WELL-202B"},
                        "limit": {"type": "integer", "default": 24, "description": "Number of recent rows to return"},
                    },
                    "required": ["asset_id"],
                },
                output_shape={
                    "type": "array",
                    "items": {
                        "timestamp": "ISO8601 string",
                        "pressure_psi": "float",
                        "temperature_c": "float",
                        "status": "string: NORMAL | CAUTION | ANOMALY",
                    },
                },
            ),
            ToolDefinition(
                name="query_risk_metrics",
                description="Query the latest risk assessment scores, integrity flags, and production impact ratings for an asset.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "asset_id": {"type": "string", "description": "Asset identifier"},
                        "limit": {"type": "integer", "default": 7, "description": "Number of recent daily risk rows"},
                    },
                    "required": ["asset_id"],
                },
                output_shape={
                    "type": "array",
                    "items": {
                        "timestamp": "date string",
                        "risk_score": "float (0-100)",
                        "integrity_flag": "string: CLEAR | MONITOR | COMPROMISED",
                        "production_impact": "string: NONE | LOW | MEDIUM | HIGH",
                    },
                },
            ),
            ToolDefinition(
                name="search_legacy_share",
                description="Full-text search across the synthetic SharePoint repository for documents matching a keyword, optionally filtered by asset.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string", "description": "Search term to match in document content"},
                        "asset_id": {"type": "string", "description": "Optional asset filter (matches filename prefix)"},
                    },
                    "required": ["keyword"],
                },
                output_shape={
                    "type": "array",
                    "items": {
                        "filename": "string",
                        "snippet": "string: matching context around keyword",
                        "match_count": "integer",
                    },
                },
            ),
            ToolDefinition(
                name="list_legacy_documents",
                description="List all documents in the synthetic SharePoint repository, optionally filtered by asset prefix.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "asset_id": {"type": "string", "description": "Optional asset prefix filter"},
                    },
                    "required": [],
                },
                output_shape={
                    "type": "array",
                    "items": {"filename": "string", "size_bytes": "integer"},
                },
            ),
            ToolDefinition(
                name="query_maintenance_history",
                description="Query historical maintenance events for an asset from the work order database.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "asset_id": {"type": "string", "description": "Asset identifier"},
                        "limit": {"type": "integer", "default": 10},
                    },
                    "required": ["asset_id"],
                },
                output_shape={
                    "type": "array",
                    "items": {
                        "event_date": "string",
                        "event_type": "string",
                        "notes": "string",
                    },
                },
            ),
        ]

    def _define_resources(self) -> List[ResourceDefinition]:
        return [
            ResourceDefinition(
                uri="legacy://sharepoint/compliance_framework.md",
                name="Operational Safety & Compliance Framework",
                description="Governance resource defining safety bounds, escalation triggers, and restart validation requirements.",
                mime_type="text/markdown",
            ),
            ResourceDefinition(
                uri="legacy://sharepoint/WELL-202B_historical_integrity_2018.txt",
                name="WELL-202B Historical Integrity Assessment 2018",
                description="Critical legacy document describing micro-fracture history and successful mitigation workflow.",
                mime_type="text/plain",
            ),
        ]

    # ------------------------------------------------------------------
    # Request Router
    # ------------------------------------------------------------------

    def handle(self, request: MCPRequest) -> MCPResponse:
        """Route an MCP request to the appropriate handler."""
        start = time.perf_counter()

        if request.method == MCPMethod.TOOLS_LIST:
            result = self._handle_tools_list()
        elif request.method == MCPMethod.TOOLS_CALL:
            result = self._handle_tools_call(request.params)
        elif request.method == MCPMethod.RESOURCES_LIST:
            result = self._handle_resources_list()
        elif request.method == MCPMethod.RESOURCES_READ:
            result = self._handle_resources_read(request.params)
        elif request.method == MCPMethod.INITIALIZE:
            result = {"server": config.MCP_SERVER_NAME, "version": config.MCP_VERSION}
        else:
            return MCPResponse(
                id=request.id,
                error={"code": -32601, "message": f"Method not found: {request.method}"},
            )

        elapsed = (time.perf_counter() - start) * 1000
        if isinstance(result, dict) and "execution_time_ms" not in result:
            result["execution_time_ms"] = round(elapsed, 2)

        return MCPResponse(id=request.id, result=result)

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _handle_tools_list(self) -> Dict[str, Any]:
        return {
            "tools": [
                {
                    "name": t.name,
                    "description": t.description,
                    "inputSchema": t.input_schema,
                    "outputShape": t.output_shape,
                }
                for t in self._tools
            ]
        }

    def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "query_modern_telemetry":
            data = self._tool_query_telemetry(arguments)
        elif tool_name == "query_risk_metrics":
            data = self._tool_query_risk(arguments)
        elif tool_name == "search_legacy_share":
            data = self._tool_search_legacy(arguments)
        elif tool_name == "list_legacy_documents":
            data = self._tool_list_legacy(arguments)
        elif tool_name == "query_maintenance_history":
            data = self._tool_query_maintenance(arguments)
        else:
            return {"status": "error", "error": f"Unknown tool: {tool_name}"}

        return {
            "status": "success",
            "tool_name": tool_name,
            "arguments": arguments,
            "data": data,
            "data_lineage": {
                "source_system": "SQLite" if "query" in tool_name else "synthetic_sharepoint",
                "source_path": str(self.db_path) if "query" in tool_name else str(self.sharepoint_dir),
                "retrieval_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        }

    def _handle_resources_list(self) -> Dict[str, Any]:
        return {
            "resources": [
                {"uri": r.uri, "name": r.name, "description": r.description, "mimeType": r.mime_type}
                for r in self._resources
            ]
        }

    def _handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        uri = params.get("uri", "")
        if uri == "legacy://sharepoint/compliance_framework.md":
            path = self.sharepoint_dir / "compliance_framework.md"
            content = path.read_text(encoding="utf-8") if path.exists() else ""
        elif uri == "legacy://sharepoint/WELL-202B_historical_integrity_2018.txt":
            path = self.sharepoint_dir / "WELL-202B_historical_integrity_2018.txt"
            content = path.read_text(encoding="utf-8") if path.exists() else ""
        else:
            return {"status": "error", "error": f"Resource not found: {uri}"}

        return {
            "status": "success",
            "uri": uri,
            "content": content,
            "data_lineage": {
                "source_system": "synthetic_sharepoint",
                "source_path": str(path),
                "retrieval_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        }

    # ------------------------------------------------------------------
    # Tool Implementations
    # ------------------------------------------------------------------

    def _tool_query_telemetry(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        asset_id = args["asset_id"]
        limit = args.get("limit", 24)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT asset_id, timestamp, pressure_psi, temperature_c, status
            FROM asset_telemetry
            WHERE asset_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (asset_id, limit),
        )
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def _tool_query_risk(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        asset_id = args["asset_id"]
        limit = args.get("limit", 7)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT asset_id, timestamp, risk_score, integrity_flag, production_impact
            FROM risk_metrics
            WHERE asset_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (asset_id, limit),
        )
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def _tool_search_legacy(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        keyword = args.get("keyword", "").lower()
        asset_id = args.get("asset_id")
        results = []

        for filepath in sorted(self.sharepoint_dir.iterdir()):
            if not filepath.is_file():
                continue
            if asset_id and not filepath.name.startswith(asset_id):
                continue

            content = filepath.read_text(encoding="utf-8", errors="ignore")
            content_lower = content.lower()
            count = content_lower.count(keyword)

            if count > 0:
                # Extract snippet around first occurrence
                idx = content_lower.find(keyword)
                start = max(0, idx - 120)
                end = min(len(content), idx + len(keyword) + 120)
                snippet = content[start:end].replace("\n", " ")
                results.append({
                    "filename": filepath.name,
                    "snippet": f"...{snippet}...",
                    "match_count": count,
                })

        return sorted(results, key=lambda x: x["match_count"], reverse=True)

    def _tool_list_legacy(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        asset_id = args.get("asset_id")
        results = []
        for filepath in sorted(self.sharepoint_dir.iterdir()):
            if not filepath.is_file():
                continue
            if asset_id and not filepath.name.startswith(asset_id):
                continue
            results.append({"filename": filepath.name, "size_bytes": filepath.stat().st_size})
        return results

    def _tool_query_maintenance(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        asset_id = args["asset_id"]
        limit = args.get("limit", 10)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT asset_id, event_date, event_type, notes
            FROM maintenance_events
            WHERE asset_id = ?
            ORDER BY event_date DESC
            LIMIT ?
            """,
            (asset_id, limit),
        )
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows
