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