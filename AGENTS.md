# AGENTS.md

## Cursor Cloud specific instructions

This repository is a personal portfolio of independent micro-projects spread across Git branches. The `main` branch contains only a README placeholder.

### Repository structure
- Each feature branch is a standalone project (no shared infrastructure)
- Python projects: Telegram bots (telethon, python-telegram-bot)
- HTML projects: Static landing pages (zero dependencies)

### Development notes
- No build system, no CI/CD, no Docker setup
- Python projects use `pip install -r requirements.txt` (in their respective branches)
- HTML projects are static files that can be served with any HTTP server
- Node.js is available in the environment for running JavaScript analysis/utilities
