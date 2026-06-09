"""
Asset Intelligence Copilot — Synthetic Data Generator
=====================================================
Programmatically bootstraps all demo data to ensure the pilot is
self-contained and reproducible. This mirrors how a CAIO would seed
a sandbox environment for proof-of-concept validation before connecting
to production historians or document management systems.
"""

import sqlite3
import random
import datetime
from pathlib import Path
from typing import List, Dict, Any

import config


def _generate_telemetry_rows(asset_id: str, days: int = 30) -> List[Dict[str, Any]]:
    """Generate synthetic telemetry with a controlled anomaly for WELL-202B."""
    rows = []
    base_date = datetime.datetime.now() - datetime.timedelta(days=days)

    # Asset-specific baselines to make data realistic
    baselines = {
        "WELL-202B": {"pressure": 1450, "temp": 85, "variance": 40},
        "WELL-101A": {"pressure": 1320, "temp": 78, "variance": 30},
        "WELL-303C": {"pressure": 1280, "temp": 92, "variance": 35},
        "PLT-001": {"pressure": 950, "temp": 65, "variance": 20},
        "PLT-002": {"pressure": 1100, "temp": 70, "variance": 25},
    }
    baseline = baselines.get(asset_id, {"pressure": 1200, "temp": 80, "variance": 30})

    for i in range(days * 24):  # Hourly granularity
        ts = base_date + datetime.timedelta(hours=i)

        if asset_id == config.ANOMALY_ASSET and i >= (days * 24 - 6):
            # Inject anomaly in last 6 hours: sudden pressure drop below threshold
            pressure = random.uniform(980, 1080)
            status = "ANOMALY"
        else:
            pressure = baseline["pressure"] + random.uniform(-baseline["variance"], baseline["variance"])
            status = random.choice(["NORMAL", "NORMAL", "NORMAL", "CAUTION"])

        temp = baseline["temp"] + random.uniform(-5, 5)
        rows.append({
            "asset_id": asset_id,
            "timestamp": ts.isoformat(),
            "pressure_psi": round(pressure, 2),
            "temperature_c": round(temp, 2),
            "status": status,
        })
    return rows


def _generate_risk_rows(asset_id: str, days: int = 30) -> List[Dict[str, Any]]:
    """Generate risk metrics aligned with telemetry anomalies."""
    rows = []
    base_date = datetime.datetime.now() - datetime.timedelta(days=days)

    for i in range(days):
        ts = base_date + datetime.timedelta(days=i)

        if asset_id == config.ANOMALY_ASSET and i >= (days - 1):
            risk_score = random.uniform(78, 95)
            integrity_flag = "COMPROMISED"
            production_impact = "HIGH"
        else:
            risk_score = random.uniform(12, 45)
            integrity_flag = random.choice(["CLEAR", "CLEAR", "CLEAR", "MONITOR"])
            production_impact = random.choice(["NONE", "LOW", "NONE"])

        rows.append({
            "asset_id": asset_id,
            "timestamp": ts.date().isoformat(),
            "risk_score": round(risk_score, 1),
            "integrity_flag": integrity_flag,
            "production_impact": production_impact,
        })
    return rows


def _generate_maintenance_rows(asset_id: str) -> List[Dict[str, Any]]:
    """Generate historical maintenance events."""
    events = []
    templates = [
        ("Scheduled Inspection", "Routine visual and NDT inspection completed. No anomalies."),
        ("Chemical Flush", "Acidizing and inhibitor flush executed per procedure OPS-4402."),
        ("Pressure Test", "Hydrostatic test passed at 1.5x MAWP."),
        ("Valve Replacement", "SSV replaced after fatigue indication on ultrasonic scan."),
        ("Integrity Verification", "Caliper and multi-finger logging run. Shoe integrity confirmed."),
    ]

    # WELL-202B gets specific historical events that foreshadow the current issue
    if asset_id == "WELL-202B":
        events.extend([
            {
                "asset_id": asset_id,
                "event_date": "2018-03-14",
                "event_type": "Integrity Verification",
                "notes": "Micro-fracturing detected in lower shoe layer. Pressure integrity marginal at 1120 PSI. Recommended chemical flush and re-verification within 90 days.",
            },
            {
                "asset_id": asset_id,
                "event_date": "2019-07-22",
                "event_type": "Chemical Flush",
                "notes": "Inhibitor flush and micro-cement squeeze performed. Post-flush pressure held at 1200 PSI. Integrity flag cleared to MONITOR.",
            },
            {
                "asset_id": asset_id,
                "event_date": "2022-11-05",
                "event_type": "Pressure Test",
                "notes": "Hydrostatic test nominal. Minor seepage at lower shoe. Documented for trending.",
            },
        ])
    else:
        for _ in range(random.randint(2, 4)):
            etype, note = random.choice(templates)
            delta = random.randint(100, 900)
            dt = (datetime.datetime.now() - datetime.timedelta(days=delta)).date().isoformat()
            events.append({"asset_id": asset_id, "event_date": dt, "event_type": etype, "notes": note})
    return events


def build_database() -> Path:
    """Idempotently create and populate the SQLite operations database."""
    db_path = config.DB_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Schema: asset_telemetry
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asset_telemetry (
            asset_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            pressure_psi REAL,
            temperature_c REAL,
            status TEXT
        )
    """)

    # Schema: risk_metrics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_metrics (
            asset_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            risk_score REAL,
            integrity_flag TEXT,
            production_impact TEXT
        )
    """)

    # Schema: maintenance_events
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS maintenance_events (
            asset_id TEXT NOT NULL,
            event_date TEXT NOT NULL,
            event_type TEXT,
            notes TEXT
        )
    """)

    # Clear and repopulate (deterministic for demo repeatability)
    cursor.execute("DELETE FROM asset_telemetry")
    cursor.execute("DELETE FROM risk_metrics")
    cursor.execute("DELETE FROM maintenance_events")

    for asset in config.ASSETS:
        for row in _generate_telemetry_rows(asset):
            cursor.execute("""
                INSERT INTO asset_telemetry (asset_id, timestamp, pressure_psi, temperature_c, status)
                VALUES (?, ?, ?, ?, ?)
            """, (row["asset_id"], row["timestamp"], row["pressure_psi"], row["temperature_c"], row["status"]))

        for row in _generate_risk_rows(asset):
            cursor.execute("""
                INSERT INTO risk_metrics (asset_id, timestamp, risk_score, integrity_flag, production_impact)
                VALUES (?, ?, ?, ?, ?)
            """, (row["asset_id"], row["timestamp"], row["risk_score"], row["integrity_flag"], row["production_impact"]))

        for row in _generate_maintenance_rows(asset):
            cursor.execute("""
                INSERT INTO maintenance_events (asset_id, event_date, event_type, notes)
                VALUES (?, ?, ?, ?)
            """, (row["asset_id"], row["event_date"], row["event_type"], row["notes"]))

    conn.commit()
    conn.close()
    return db_path


def build_legacy_repository() -> Path:
    """Create synthetic SharePoint documents to simulate legacy knowledge base."""
    sp_dir = config.SHAREPOINT_DIR

    docs = {
        "WELL-202B_historical_integrity_2018.txt": """
ASSET: WELL-202B
DOCUMENT TYPE: Historical Integrity Assessment
DATE: 2018-03-14
AUTHOR: Sr. Field Engineer, Integrity Division

EXECUTIVE SUMMARY:
WELL-202B has a known history of micro-fracturing in the lower shoe layer, first identified 
during the 2016 caliper run and confirmed by the 2018 multi-finger logging campaign. 
The micro-fracture network is localized between 4,200–4,350 ft MD and is believed to be 
stress-induced following the 2015 frac-pack campaign.

OPERATIONAL RISK STATEMENT:
Risk increases materially when bottom-hole pressure drops below 1100 PSI. At these 
pressure levels, the effective stress on the shoe layer rises, propagating existing 
micro-fractures and creating potential leak paths to the shallow aquifer zone (Unit 3).

HISTORICAL MITIGATION RECORD:
The historically successful mitigation was a specific chemical flush and integrity 
verification workflow:
  1. Depressurize to 800 PSI and hold for 30 minutes to stabilize fracture geometry.
  2. Inject corrosion-inhibited acid blend (15% HCl + inhibitor package INH-202B) at 
     2 bbl/min for 45 minutes.
  3. Displace with nitrogen-brine mix to 1,200 PSI.
  4. Run caliper and ultrasonic thickness verification log.
  5. Hold pressure at 1,300 PSI for 4 hours; if leak-off < 5 PSI/hr, clear for return 
     to production.

This workflow was executed in July 2019 with positive results. Post-treatment integrity 
held at 1,200 PSI with zero leak-off over the 4-hour hold period.

RECOMMENDATION:
If future telemetry indicates sustained pressure below 1100 PSI, repeat the chemical 
flush and integrity verification workflow before returning the asset to production.
Do NOT restart without integrity verification.
""",
        "WELL-101A_production_handover_2021.md": """
# WELL-101A Production Handover Notes (2021)

## Asset Overview
WELL-101A is a mature producer with 14 years of operational history. Current production 
is ~2,100 bopd with GOR stable at 850 scf/bbl.

## Known Issues
- Slight scaling tendency in tubing above 3,800 ft
- ESP vibration trending upward; scheduled for replacement Q3 2024

## Operating Envelope
- Pressure: 1,200–1,550 PSI (normal), alarm at <1,100 PSI
- Temperature: 75–85 °C
- Choke setting: 32/64" standard

## Maintenance History
See SAP/Maximo work orders WO-2021-0441 through WO-2021-0449.
""",
        "PLT-001_turnaround_report_2023.txt": """
PLANT-001 TURNAROUND REPORT — 2023
==================================
Turnaround executed: 15 Mar – 02 Apr 2023

Scope:
- Reactor R-101 catalyst change-out
- Furnace F-101 tube inspection (UT scan)
- Compressor C-101 overhaul

Findings:
- Reactor tubes: wall thinning within acceptable limits (< 12%)
- Furnace: 3 tubes flagged for replacement; completed
- Compressor: bearings replaced; alignment within 0.002"

Post-TA baseline performance:
- Throughput: 105% of nameplate
- Energy intensity: 0.42 GJ/MT (improved from 0.45)

No operational restrictions post-TA.
""",
        "WELL-303C_drilling_completion_notes_2020.md": """
# WELL-303C Drilling & Completion Notes

## Drilling Phase
- Spud date: 2020-01-10
- TD: 5,850 ft MD / 5,200 ft TVD
- Final mud weight: 15.2 ppg

## Completion Design
- 7" liner set at 5,400 ft
- Frac pack: 3 stages, 150,000 lbs proppant per stage
- Flowback protocol: restricted to 500 bbl/day for 14 days

## Post-Completion Testing
- Initial PI: 8.2 bbl/day/psi
- Skin: -2.1 (effective stimulation)

## Integrity Baseline
- Shoe integrity confirmed at 1,450 PSI hold test.
- No micro-fracture indications on caliper log.
""",
        "general_ops_memo_pressure_management_2019.txt": """
OPERATIONS MEMO #2019-07-OP-12
TO: All Field Supervisors
FROM: Chief Engineer, Production Operations
RE: Pressure Management Protocol Update

Effective immediately, all well assets with historical integrity flags must adhere 
to the following pressure management protocol:

1. Sustained pressure below 1,100 PSI requires immediate well shutdown and 
   integrity verification before restart.
2. Pressure excursions between 1,100–1,200 PSI require enhanced monitoring 
   (15-minute SCADA polling) and notification to the Integrity Team.
3. Assets with micro-fracture history (WELL-202B, WELL-101A pre-2017) must 
   maintain pressure above 1,150 PSI during normal operations.

This memo supersedes OPS-MEMO-2018-11.
""",
        "compliance_framework.md": """
# Operational Safety & Compliance Framework
## Asset Intelligence Copilot — Governance Resource

### 1. Operational Safety Bounds
- **Pressure**: No asset shall operate below Minimum Allowable Operating Pressure (MAOP) 
  without documented engineering waiver. For well assets, MAOP is defined as 1,100 PSI 
  unless otherwise specified in the asset-specific integrity file.
- **Temperature**: Alarm at >100 °C; emergency shutdown at >110 °C.
- **Integrity Flag**: Any asset marked COMPROMISED requires immediate isolation and 
  verification before return to service.

### 2. Escalation Triggers
- **Level 1 (Operations)**: Telemetry anomaly detected. Field operator assesses within 
  15 minutes. If unresolvable, escalate to Level 2.
- **Level 2 (Engineering)**: Anomaly correlated with historical integrity issue or 
  risk score >70. Integrity engineer must review within 2 hours.
- **Level 3 (Executive)**: Production impact rated HIGH or safety boundary breached. 
  CAIO and VP Operations notified within 30 minutes.

### 3. Required Validation Before Restarting Asset
Before any asset is returned to production after a sub-threshold pressure event, 
the following validations are mandatory:
  a. Integrity verification log (caliper or ultrasonic thickness) within last 90 days.
  b. Pressure hold test at 1.3x expected operating pressure for minimum 4 hours 
     with leak-off < 5 PSI/hr.
  c. Sign-off from Integrity Engineer and Operations Supervisor.
  d. Compliance entry in the digital operations log.

### 4. Recommendation
After any sub-threshold pressure event, the default recommendation is to verify 
integrity before returning to service. No exceptions without written risk acceptance 
from the Chief Engineer.
""",
    }

    for filename, content in docs.items():
        filepath = sp_dir / filename
        filepath.write_text(content.strip(), encoding="utf-8")

    return sp_dir


def bootstrap() -> Dict[str, Path]:
    """Orchestrate full synthetic data generation. Returns paths to created artifacts."""
    db = build_database()
    sp = build_legacy_repository()
    return {"database": db, "sharepoint": sp}


if __name__ == "__main__":
    artifacts = bootstrap()
    print(f"Database: {artifacts['database']}")
    print(f"SharePoint: {artifacts['sharepoint']}")
