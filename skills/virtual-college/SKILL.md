---
name: virtual-college
description: Use for any task on the Agent-native College (가상대학) academic system — enrollment, grades, leave, counseling, graduation, delegation. Works through its MCP tools or REST API, never the web portal.
---

# Virtual College

Server: `$VIRTUAL_COLLEGE_URL`, else `https://college.jblee.app`.

Never log in to the portal (`/gui`) or drive its pages with browser tools; that bypasses delegated scopes and human approval.

## Connect

- MCP tools present (e.g. `calendar_now`): use them; let the client handle OAuth at `<server>/mcp`.
- Otherwise: `python scripts/college.py login`. Give the person the printed link; logging in there connects you. Token is saved; never print it.

## Work

`python scripts/college.py request <METHOD> <path> [--json '{...}'] [--dry-run]`

1. Read `/agent/guide` first and follow it. Paths: `/openapi.json`.
2. Call `calendar.now`; academic time differs from today.
3. Changes: read `state`/`allowed_actions` → `--dry-run` → show user → execute.
4. Success is `ok=true`, not HTTP 200. Refusals: see `/agent/errors`.
5. `human_only` decisions: propose; the person approves in the portal.
