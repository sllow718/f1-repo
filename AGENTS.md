# AGENTS.md

## Project Context

This repository contains an F1 simulator/telemetry project for Raspberry Pi and Linux environments. It listens for F1 game UDP telemetry and can store or forward packets using local logging or pickle files, RabbitMQ, Oracle Autonomous Database, and a Flask-based web UI.

This codebase was originally working. Codex was added to help diagnose and resolve an issue without disturbing the existing working setup. Treat the current files, versions, local configuration, services, wallets, and environment as intentional unless there is clear evidence otherwise.

Primary areas:

- `src/` - simulator, packet handling, storage, RabbitMQ, Oracle DB, UDP, and health-check logic.
- `web/` - Flask web application and related models/admin/session code.
- `bin/` - install, setup, service, runtime, RabbitMQ, wallet, security, and maintenance scripts.
- `migrations/` - database migration support.
- `test/` - packet regression/debug scripts and local test utilities.

## Core Working Rules

- Make the smallest practical change needed to fix the requested issue.
- Preserve existing behavior unless the issue requires changing it.
- Do not perform broad refactors, formatting churn, dependency upgrades, cleanup passes, or file reorganizations unless explicitly requested.
- Do not delete files randomly or remove files just because they appear generated, old, unused, or unfamiliar.
- Do not overwrite existing settings, generated files, wallet files, service files, credentials, local virtualenvs, logs, or user configuration unless the user explicitly approves it.
- Prefer reading and understanding the existing code path before changing anything.
- If a change is risky or touches setup, services, database access, wallet handling, or credentials, explain the risk and ask before proceeding.

## Safety Rules

- Do not print, expose, commit, or modify secrets from `f1store.yaml`, `.f1sim_secret`, `.ssh/`, `Wallet_f1simdb/`, wallet zip files, or Oracle wallet files.
- Prefer templates such as `f1store.yaml.template` and `f1env.sh.template` when documenting configuration.
- Ask before running commands that use `sudo`, `systemctl`, RabbitMQ admin commands, Oracle DB connections, wallet setup/update scripts, service install scripts, or destructive shell operations.
- Ask before installing, uninstalling, or upgrading packages with tools such as `apt`, `pip`, `npm`, or similar package managers.
- Do not install packages in a way that may overwrite previous versions or environment settings unless the user explicitly approves it.

## Development Workflow

- Use Python 3 and the existing project environment when possible.
- Activate the local virtual environment with `source dev/bin/activate` when it is appropriate and available.
- Use `requirements.txt` or `requirements_nopi.txt` only when dependency installation is explicitly approved.
- Main runtime commands documented by the project include:
  - `python3 src/main.py produce`
  - `python3 src/main.py consume`
  - scripts under `bin/` for service, webserver, setup, start, and stop workflows.
- Keep shell commands narrow and inspect-only by default.

## Verification

- For code changes, run the narrowest relevant local check or test script from `test/` when safe.
- Avoid hardware, service, RabbitMQ, Oracle DB, wallet, or system-level verification unless the user explicitly approves it.
- If verification cannot be run safely, state exactly what was not run and why.

## Persistent Change Logging Requirements

For every required change to files or folders in this repository, append a specific change log entry to `codexactionlogs.txt` in the repository root. This log file is the persistent record of Codex actions in this folder and should be updated as part of the same work whenever any file or folder is created, modified, moved, or deleted.

Each log entry must make rollback straightforward. Include:

- File path changed.
- Reason for the change.
- What the previous behavior or content was.
- What it was changed to.
- Any commands run to verify the change.
- Any commands intentionally not run because they were risky, destructive, or required approval.

When exact previous content is long, summarize the previous behavior precisely and rely on the patch or local file history for exact rollback details. Do not hide meaningful changes behind vague summaries.

Log entries should be written before final response. If a verification command is expected to be run after the log entry is written, record that command in the entry and then run it. If verification fails or causes another change, append a follow-up entry.
