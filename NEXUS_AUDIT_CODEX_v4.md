# NEXUS AUDIT CODEX v4

## 1. Overview
The Nexus Audit Tool is a modular package for auditing Django-based applications. It performs static analysis, dependency vulnerability scanning, and AI-driven refactoring recommendations.

## 2. Architecture
The tool is structured as a Python package (`nexus_audit/`) with a clear separation between:
- **Scanners:** Static analysis (Bandit, Vulture, Radon).
- **AI Backend:** Orchestrates AI-powered analysis (Gemini, Ollama, Claude).
- **Features:** Decoupling tools (Fix Queue, Coupling Maps, Timeline).
- **Report Generator:** Interactive HTML dashboard using `vis-network`.

## 3. Workflow
1.  **Sync:** `pulse` command synchronizes live codebase.
2.  **Scan:** Tool maps physical structure and scans for violations/dependencies.
3.  **Analyze:** AI analyzes high-impact violations.
4.  **Report:** Interactive dashboard displays actionable recommendations.

## 4. Maintenance
- **Adding Features:** New features must be injected into the dashboard via the stable 'report/dashboard_template.html' rather than fragile string replacement.
- **Cleanup:** Regularly remove temporary analysis files and old backups.
- **Dependencies:** Update `requirements.txt` based on Tier 2 vulnerability scans.
