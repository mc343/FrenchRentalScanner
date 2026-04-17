"""Test Vercel deployment configuration."""

import json
import os
from pathlib import Path


def test_vercel_json_exists():
    """Test that vercel.json exists in project root."""
    project_root = Path(__file__).parent.parent
    vercel_json_path = project_root / "vercel.json"
    assert vercel_json_path.exists(), "vercel.json must exist in project root"


def test_vercel_json_structure():
    """Test that vercel.json has correct structure."""
    project_root = Path(__file__).parent.parent
    vercel_json_path = project_root / "vercel.json"

    with open(vercel_json_path, 'r') as f:
        config = json.load(f)

    # Test version
    assert config["version"] == 2, "vercel.json must use version 2"

    # Test builds
    assert "builds" in config, "vercel.json must have builds array"
    assert len(config["builds"]) == 1, "Must have exactly one build configuration"

    build = config["builds"][0]
    assert build["src"] == "api/index.py", "Build source must be api/index.py"
    assert build["use"] == "@vercel/python", "Must use @vercel/python runtime"

    # Test routes
    assert "routes" in config, "vercel.json must have routes array"
    assert len(config["routes"]) == 1, "Must have exactly one route"

    route = config["routes"][0]
    assert route["src"] == "/(.*)", "Route pattern must match all paths"
    assert route["dest"] == "api/index.py", "Route destination must be api/index.py"


def test_vercelignore_exists():
    """Test that .vercelignore exists."""
    project_root = Path(__file__).parent.parent
    vercelignore_path = project_root / ".vercelignore"
    assert vercelignore_path.exists(), ".vercelignore must exist in project root"


def test_vercelignore_content():
    """Test that .vercelignore excludes correct files."""
    project_root = Path(__file__).parent.parent
    vercelignore_path = project_root / ".vercelignore"

    with open(vercelignore_path, 'r') as f:
        content = f.read()

    # Check that required exclusions are present
    required_exclusions = [
        "__pycache__/",
        "*.pyc",
        ".pytest_cache/",
        "tests/",
        "*.db"
    ]

    for exclusion in required_exclusions:
        assert exclusion in content, f".vercelignore must exclude {exclusion}"


def test_api_directory_structure():
    """Test that api directory exists (will be used in Task 9)."""
    project_root = Path(__file__).parent.parent
    api_dir = project_root / "api"
    assert api_dir.exists(), "api directory must exist for WSGI adapter"
    assert api_dir.is_dir(), "api must be a directory"
