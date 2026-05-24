# Nexus Audit Tool: Comprehensive Operations Guide

This document is the complete operational manual for the Nexus Audit Tool. It explains exactly how the tool works, how to run it, how to adapt it to any arbitrary Python/Django project, and what fallback mechanisms are built into its architecture.

---

## 1. How It Runs (The Core Architecture)

When you execute the tool, it follows a strict sequence of operations to analyze a project without altering any of the target project's code:

1. **Physical Discovery (DNA Mapping):** It recursively scans the target project path, mapping out every `.py` file. It parses Abstract Syntax Trees (ASTs) to map every import statement, tracking boundaries between first-party apps, standard libraries, and third-party dependencies.
2. **Static Analysis (Tier 1):** It runs multi-threaded scanners. It uses Bandit to find security issues, Vulture to identify dead code, and Radon (if installed) to calculate cyclomatic complexity. It also checks for circular dependencies (cycles) and "ghost files" (missing imports).
3. **Dependency Scanning (Tier 2):** If an internet connection is detected, it reads the target project's `requirements.txt`. It queries PyPI for outdated packages and the Google OSV database for known CVE vulnerabilities.
4. **AI Analysis:** It routes the gathered violations to an AI backend (Ollama, Gemini, or Claude). The AI writes personalized, context-aware refactoring advice, security fixes, and architectural extraction plans.
5. **Dashboard Generation:** It compiles all this data into `master_nexus_dna.json` and renders an interactive HTML dashboard (`visuals/NEXUS_AUDIT_DASHBOARD.html`) with a dynamic dependency map.

---

## 2. Execution Modes (How to Run It)

The tool is executed via the `pulse.py` wrapper at the root of the audit tool directory.

| Command | Purpose |
| :--- | :--- |
| `python pulse.py` | **Full Audit:** Runs the complete end-to-end audit (Tier 1, Tier 2, and AI processing). Takes the longest but provides the deepest insights. |
| `python pulse.py --fast` | **Fast Delta Mode:** Uses `git diff` to only analyze files that have changed since the last commit. Bypasses the AI and network scans. Perfect for running as a pre-commit hook or doing quick local sanity checks. |
| `python pulse.py --serve` | **Server Mode:** Runs a full audit, and then immediately spins up a local web server (typically `http://localhost:8421`) to host the interactive HTML dashboard. |
| `python pulse.py --serve --watch`| **Live Server Mode:** Runs the server and watches the target project's file system. If you save a file in your target project, it re-runs the audit in the background and hot-reloads the dashboard automatically. |
| `python pulse.py --install-hook`| **Pre-commit Setup:** Installs `--fast` mode into the target project's `.git/hooks/pre-commit` to prevent committing boundary violations. |

---

## 3. Can it run on ANY project?

**Yes, but it requires minor configuration adjustments.** 

By default, the tool is heavily optimized for a specific Django project (the "Nexus" ecosystem). It attempts to be smart: it will search the target project for a `settings.py` file, read the `INSTALLED_APPS` list, and look for any apps that start with `nexus_` to determine what the "first-party" boundaries are. 

If you want to point this tool at a completely different, non-Nexus project, you must change a few hardcoded settings in the tool's core configuration.

### What You Need to Change (`nexus_audit/nexus_audit/config.py`):

1. **The Target Path:**
   Change the `PROJECT_PATH` variable to point to the root directory of your new target project.
   ```python
   PROJECT_PATH = os.path.expanduser('~/path/to/your/new_project')
   ```

2. **The First-Party App Fallback:**
   If the tool cannot dynamically find your Django `settings.py`, it falls back to a hardcoded list. You must change this list to match the core folders/apps of your specific project:
   ```python
   FIRST_PARTY_APPS_FALLBACK = [
       'my_app_core', 'my_app_auth', 'my_app_billing'
   ]
   ```

3. **Dependency Scanning Paths:**
   Update `_REQ_TXT_PATHS` to point to the `requirements.txt` of the new project, otherwise, Tier 2 scanning will fail to find your installed packages.
   ```python
   _REQ_TXT_PATHS = [
       os.path.join(PROJECT_PATH, 'requirements.txt')
   ]
   ```

4. **Django vs Standard Python:**
   If your new project is **not** a Django project, you should update the `DJANGO_ACCEPTABLE` whitelist in `config.py` to include whatever frameworks your new project uses (like `flask`, `fastapi`, or `sqlalchemy`) so the tool knows those imports are safe framework dependencies and not cross-app violations.

---

## 4. The Fallback Architecture (Safety Nets)

The tool is designed with a "graceful degradation" philosophy. If a system fails, it falls back to a safe alternative rather than crashing.

> **Internet/Network Fallback**
> If you run the tool on an airplane with zero Wi-Fi, it will detect the lack of internet instantly. It skips the Tier 2 CVE vulnerability scanning (OSV) and PyPI freshness checks, and proceeds to finish the static analysis entirely offline.

> **AI Backend Fallback**
> The tool searches for AI capabilities in this priority order:
> 1. **Ollama:** Checks `localhost:11434`. If found, runs locally (Free, unlimited, offline).
> 2. **Gemini:** Checks `.env` for `GEMINI_API_KEY`. (Free, high quality, but has rate limits).
> 3. **Claude:** Checks `.env` for `ANTHROPIC_API_KEY`. (Paid, highest quality).
> 4. **Templates (No AI):** If absolutely no AI is available, the tool falls back to Tier-1 hardcoded template recommendations, still giving you actionable advice based on regex patterns.

> **API Rate Limiting Fallback (`KeyPool`)**
> If you are using Gemini's free tier, you will eventually hit a `429 Too Many Requests` error. The tool's `KeyPool` system catches this:
> - If it's a **per-minute (RPM) limit**, it either rotates to a backup API key (`GEMINI_API_KEY_2`) or pauses the program safely for 65 seconds to let the quota cool down.
> - If it's a **Daily Limit**, it marks that specific model/key as exhausted for the rest of the run and forces the system to try the next available model in the list.

> **Django Settings Fallback**
> If the `audit_engine.py` fails to dynamically import and parse the target project's `settings.py` due to syntax errors or missing environment variables in the target project, it catches the exception and gracefully reverts to using the `FIRST_PARTY_APPS_FALLBACK` string list defined in `config.py`.
