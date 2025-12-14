# WireGuard GUI

A modern, beautiful, cross-platform WireGuard GUI using Python + PySide6.

## Features

- **System Tray Integration**: Persistent tray icon with status indicators (Green for Connected, Red/No Internet for Disconnected).
- **Network Safety**: Built-in Network Backup & Restore to prevent configuration mishaps.
- **Modern UI**: Dark/Light themes and profile management.
- **Secure Storage**: Profiles are stored securely (permissions restricted).
- **Cross-platform**: Designed for Linux and Windows.

## Requirements

- Python 3.11+
- WireGuard tools (`wg`, `wg-quick`) installed on the system.
- Root/Admin privileges (required for WireGuard and Network Backup).

## Installation & Running

This project uses `uv` for dependency management, but can also be installed with `pip`.

### Using pip

1. Install the package in editable mode:
   ```bash
   pip install -e .
   ```
2. Run the application (must be run as root/admin for VPN functionality):
   ```bash
   sudo python src/main.py
   ```

### Using uv

1. Sync dependencies:
   ```bash
   uv sync
   ```
2. Run:
   ```bash
   uv run src/main.py
   ```
