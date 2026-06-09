"""
Asset Intelligence Copilot — Configuration Module
=================================================
Centralizes all runtime configuration, paths, and constants.
This pattern allows the Chief AI Officer to inject environment-specific
settings (dev, staging, prod) without touching business logic.
"""

import os
from pathlib import Path

# Project root: config.py lives in src/, so project root is one level up
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"
SHAREPOINT_DIR = PROJECT_ROOT / "synthetic_sharepoint"
DB_PATH = DATA_DIR / "asset_ops.db"

# Ensure directories exist at import time (idempotent)
DATA_DIR.mkdir(exist_ok=True)
SHAREPOINT_DIR.mkdir(exist_ok=True)

# Synthetic data generation parameters
ASSETS = ["WELL-202B", "WELL-101A", "WELL-303C", "PLT-001", "PLT-002"]
ANOMALY_ASSET = "WELL-202B"
PRESSURE_THRESHOLD_PSI = 1100.0  # Critical threshold from legacy engineering knowledge

# MCP Server configuration (in-process)
MCP_SERVER_NAME = "asset-intelligence-mcp"
MCP_VERSION = "1.0.0"

# Agent configuration
MAX_TOOL_CALLS = 10  # Safety guardrail: prevent runaway agent loops
