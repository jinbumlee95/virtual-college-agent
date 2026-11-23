#!/usr/bin/env python3
"""Connect an agent to the Agent-native College and call its REST operations.

Standard library only, so any agent that can run Python can use it.

    python college.py login                      # link -> person logs in -> token saved
    python college.py status
    python college.py request GET /calendar/now
    python college.py request POST /path --json '{"a": 1}' --dry-run
    python college.py logout

Server: --url, else VIRTUAL_COLLEGE_URL, else https://college.jblee.app.
The token never reaches stdout; it lives in ~/.virtual-college/ with owner-only access.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import webbrowser
from pathlib import Path

DEFAULT_URL = "https://college.jblee.app"
STORE = Path.home() / ".virtual-college"


def server(args) -> str:
    return (args.url or os.environ.get("VIRTUAL_COLLEGE_URL") or DEFAULT_URL).rstrip("/")


def token_file(base: str) -> Path:
    host = urllib.parse.urlsplit(base).netloc.replace(":", "_")
    return STORE / f"{host}.json"


def http(method, url, *, body=None, token=None, headers=None):
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Accept", "application/json, text/markdown;q=0.9, */*;q=0.8")
    if data is not None:
        request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", "Bearer " + token)
    for name, value in (headers or {}).items():
        request.add_header(name, value)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status, response.headers.get("Content-Type", ""), response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.headers.get("Content-Type", ""), error.read()


def result_of(raw: bytes) -> dict:
    payload = json.loads(raw or b"{}")
    return payload.get("result", payload) if isinstance(payload, dict) else payload


def save(base: str, value: dict) -> None:
    STORE.mkdir(mode=0o700, exist_ok=True)
    path = token_file(base)
    path.write_text(json.dumps(value), encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass  # Windows keeps the file under the user's profile


def load(base: str) -> dict | None:
    path = token_file(base)
    if not path.is_file():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if value.get("expires_at", 0) > time.time() else None


def login(args) -> int:
    base = server(args)
    status, _, raw = http(
        "POST", base + "/auth/login/start", body={"client_name": args.name}
    )
    start = result_of(raw)
    if status >= 400 or "device_code" not in start:
        print(f"Could not start login at {base}: {raw.decode(errors='replace')}", file=sys.stderr)
        return 1
    link = start.get("verification_uri_complete") or start["verification_uri"]
    print(f"Ask the person to open this link and log in. Logging in connects you:\n\n  {link}\n")
    if "verification_uri_complete" not in start:
        print(f"Then enter the code {start['user_code']}.\n")
    if not args.no_browser:
        try:
            webbrowser.open(link)
        except Exception:
            pass
    interval = max(int(start.get("interval", 5)), 1)
    deadline = time.time() + int(start.get("expires_in", 600))
    print("Waiting for the person to log in...", flush=True)
    while time.time() < deadline:
        time.sleep(interval)
        _, _, raw = http(
            "POST",
            base + "/auth/login/poll",
            body={"client_id": start["client_id"], "device_code": start["device_code"]},
        )
        polled = result_of(raw)
        if "access_token" in polled:
            save(
                base,
                {
                    "server": base,
                    "access_token": polled["access_token"],
                    "scope": polled.get("scope", ""),
                    "expires_at": time.time() + int(polled.get("expires_in", 0)),
                },
            )
            days = int(polled.get("expires_in", 0)) // 86400
            scopes = len(polled.get("scope", "").split())
            print(f"Connected to {base}: {scopes} scopes, valid for {days} days.")
            return 0
        error = polled.get("error")
        if isinstance(error, dict):
            error = error.get("code")
        if error == "slow_down":
            interval += 5
        elif error not in ("authorization_pending", None):
            print(f"Login ended: {error}", file=sys.stderr)
            return 1
    print("The link expired before the person logged in. Run login again.", file=sys.stderr)
    return 1


def status(args) -> int:
    base = server(args)
    saved = load(base)
    if saved is None:
        print(f"Not connected to {base}. Run: python college.py login")
        return 1
    left = int(saved["expires_at"] - time.time())
    print(f"Connected to {base}: {len(saved['scope'].split())} scopes, {left // 3600} hours left.")
    return 0


def logout(args) -> int:
    path = token_file(server(args))
    if path.is_file():
        path.unlink()
    print("Removed the saved token. Revoke it in the portal's delegation page if needed.")
    return 0


def request(args) -> int:
    base = server(args)
    saved = load(base)
    path = args.path if args.path.startswith("/") else "/" + args.path
    headers = {}
    method = args.method.upper()
    if args.dry_run:
        path += ("&" if "?" in path else "?") + "dry_run=true"
    elif method not in ("GET", "HEAD"):
        headers["Idempotency-Key"] = args.key or str(uuid.uuid4())
    body = json.loads(args.json) if args.json is not None else None
    if body is None and method not in ("GET", "HEAD", "DELETE"):
        body = {}
    code, kind, raw = http(
        method,
        base + path,
        body=body,
        token=saved["access_token"] if saved else None,
        headers=headers,
    )
    text = raw.decode("utf-8", errors="replace")
    if "json" in kind:
        try:
            text = json.dumps(json.loads(text), ensure_ascii=False, indent=2)
        except ValueError:
            pass
    print(text)
    if code == 401 and saved is None:
        print("\nNot connected. Run: python college.py login", file=sys.stderr)
    return 0 if code < 400 else 1


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", help="Server URL (default: VIRTUAL_COLLEGE_URL or college.jblee.app)")
    commands = parser.add_subparsers(dest="command", required=True)

    start = commands.add_parser("login", help="Connect through the person's browser login")
    start.add_argument("--name", default="Agent", help="Agent name shown to the person")
    start.add_argument("--no-browser", action="store_true", help="Only print the link")
    start.set_defaults(run=login)

    commands.add_parser("status", help="Show the saved connection").set_defaults(run=status)
    commands.add_parser("logout", help="Forget the saved token").set_defaults(run=logout)

    call = commands.add_parser("request", help="Call a REST path with the saved token")
    call.add_argument("method")
    call.add_argument("path")
    call.add_argument("--json", help="JSON body")
    call.add_argument("--dry-run", action="store_true", help="Preview a change")
    call.add_argument("--key", help="Idempotency-Key to reuse when retrying the same write")
    call.set_defaults(run=request)

    args = parser.parse_args()
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
