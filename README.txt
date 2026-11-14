mumu thin client
Copyright 2026 MoonKibong (kibong.moon@gmail.com)

The client and identified first-party guides/templates use Apache-2.0.
LICENSE contains the complete terms; DISTRIBUTION-NOTICE.txt defines scope.
The private service requires separately authorized credentials and a privately
supplied URL. Downloading or building this client does not grant service access.
The site/ directory contains English and Korean guides and canonical templates.

Recipient source-build procedure:
1. Run python3.11 -m venv .venv (or use Python 3.15). Continue only if it exits zero.
2. Run .venv/bin/python -m pip --isolated install --no-cache-dir --index-url https://pypi.org/simple .
   Continue only if it exits zero. If resolution fails, stop; preserve pinned dependencies.
3. Run .venv/bin/mumu --help. Completion: help exits zero. If it fails, use site/en/troubleshoot.html.

These instructions need only this exported source and public build/runtime dependencies.
They need no private checkout, private index or private build script.
