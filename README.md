# site-health-tester

A simple pytest-based test suite to verify HTTP to HTTPS redirections, canonical domain handling (non-www to www), and HSTS header enforcement for your website.

## Description

This script automates checks for:
- Permanent 301 redirects from HTTP to HTTPS (preserving www).
- 301 redirect from HTTPS without www to HTTPS with www.
- HSTS header presence on HTTPS responses (with max-age) and absence on HTTP.
- Basic liveness check (200 OK on HTTPS).

## Requirements

- Python 3.8+ (tested on 3.14)
- `requests` and `pytest` libraries

## Setup

1. Clone or create the project directory.
2. Create a virtual environment:
   ```
   python -m venv .env
   ```
3. Activate it:
   - Linux/macOS: `source .env/bin/activate`
   - Windows: `.env\Scripts\activate`
4. Install dependencies:
   ```
   pip install requests pytest
   ```

## Usage

Run all tests:
```
pytest main.py -v
```

- `-v` for verbose output (shows pass/fail details and debug logs).
- Use `pytest main.py::test_name` to run a specific test (e.g., `test_http_to_https_redirect`).

