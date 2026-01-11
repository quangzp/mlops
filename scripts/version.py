#!/usr/bin/env python3
"""Version management script for the mlops package."""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
VERSION_FILE = PROJECT_ROOT / "mlops" / "__version__.py"
PYPROJECT_FILE = PROJECT_ROOT / "pyproject.toml"
CONFIG_FILE = PROJECT_ROOT / "mlops" / "config" / "config.yaml"
API_FILE = PROJECT_ROOT / "mlops" / "serving" / "api.py"


def get_version():
    """Read version from __version__.py."""
    with open(VERSION_FILE, "r") as f:
        content = f.read()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    raise ValueError("Could not find version in __version__.py")


def update_pyproject(version: str):
    """Update version in pyproject.toml."""
    with open(PYPROJECT_FILE, "r") as f:
        content = f.read()

    content = re.sub(
        r'version\s*=\s*["\'][^"\']+["\']',
        f'version = "{version}"',
        content,
        count=1
    )

    with open(PYPROJECT_FILE, "w") as f:
        f.write(content)
    print(f"✓ Updated {PYPROJECT_FILE} to version {version}")


def update_config_yaml(version: str):
    """Update version in config.yaml."""
    with open(CONFIG_FILE, "r") as f:
        content = f.read()

    content = re.sub(
        r'version:\s*["\']?[^"\'\n]+["\']?',
        f'version: "{version}"',
        content,
        count=1
    )

    with open(CONFIG_FILE, "w") as f:
        f.write(content)
    print(f"✓ Updated {CONFIG_FILE} to version {version}")


def update_api(version: str):
    """Update version in api.py."""
    with open(API_FILE, "r") as f:
        content = f.read()

    content = re.sub(
        r'version\s*=\s*["\'][^"\']+["\']',
        f'version="{version}"',
        content,
        count=1
    )

    with open(API_FILE, "w") as f:
        f.write(content)
    print(f"✓ Updated {API_FILE} to version {version}")


def sync_all():
    """Sync version across all files."""
    version = get_version()
    print(f"Syncing version {version} across all files...")
    update_pyproject(version)
    update_config_yaml(version)
    update_api(version)
    print(f"\n✓ All files synced to version {version}")


def bump_version(part: str):
    """Bump version (major, minor, patch)."""
    version = get_version()
    parts = version.split(".")

    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")

    major, minor, patch = map(int, parts)

    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid version part: {part}. Use 'major', 'minor', or 'patch'")

    new_version = f"{major}.{minor}.{patch}"

    # Update __version__.py
    with open(VERSION_FILE, "r") as f:
        content = f.read()

    content = re.sub(
        r'__version__\s*=\s*["\'][^"\']+["\']',
        f'__version__ = "{new_version}"',
        content
    )

    with open(VERSION_FILE, "w") as f:
        f.write(content)

    print(f"✓ Bumped version from {version} to {new_version}")

    # Sync all files
    sync_all()


def show_version():
    """Show current version."""
    version = get_version()
    print(f"Current version: {version}")
    return version


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/version.py show          - Show current version")
        print("  python scripts/version.py sync          - Sync version across all files")
        print("  python scripts/version.py bump <part>   - Bump version (major/minor/patch)")
        sys.exit(1)

    command = sys.argv[1]

    if command == "show":
        show_version()
    elif command == "sync":
        sync_all()
    elif command == "bump":
        if len(sys.argv) < 3:
            print("Error: Please specify version part (major/minor/patch)")
            sys.exit(1)
        bump_version(sys.argv[2])
    else:
        print(f"Error: Unknown command '{command}'")
        sys.exit(1)
