"""Test deployment readiness for Vercel deployment."""

import json
import os
from pathlib import Path


def test_deployment_readiness():
    """Test that all required files and configurations exist for deployment."""
    project_root = Path(__file__).parent.parent

    # Check vercel.json exists and is valid
    vercel_json_path = project_root / "vercel.json"
    assert vercel_json_path.exists(), "vercel.json must exist for deployment"

    with open(vercel_json_path, 'r') as f:
        config = json.load(f)

    assert "version" in config, "vercel.json must have version"
    assert "builds" in config, "vercel.json must have builds"
    assert "routes" in config, "vercel.json must have routes"

    # Check API entry point exists
    api_index_path = project_root / "api" / "index.py"
    assert api_index_path.exists(), "api/index.py must exist as entry point"

    # Check requirements.txt exists
    requirements_path = project_root / "requirements.txt"
    assert requirements_path.exists(), "requirements.txt must exist for dependencies"

    # Check DEPLOYMENT.md exists
    deployment_md_path = project_root / "DEPLOYMENT.md"
    assert deployment_md_path.exists(), "DEPLOYMENT.md must exist with deployment instructions"


def test_deployment_documentation_content():
    """Test that DEPLOYMENT.md contains required sections."""
    project_root = Path(__file__).parent.parent
    deployment_md_path = project_root / "DEPLOYMENT.md"

    with open(deployment_md_path, 'r') as f:
        content = f.read()

    # Check for required sections
    required_sections = [
        "# Prerequisites",
        "# Environment Variables",
        "# Deployment Steps",
        "# Troubleshooting"
    ]

    for section in required_sections:
        assert section in content, f"DEPLOYMENT.md must contain {section} section"


def test_deployment_documentation_quality():
    """Test that DEPLOYMENT.md contains key information."""
    project_root = Path(__file__).parent.parent
    deployment_md_path = project_root / "DEPLOYMENT.md"

    with open(deployment_md_path, 'r') as f:
        content = f.read()

    # Check for key deployment information
    required_keywords = [
        "Vercel",
        "environment",
        "install",
        "deploy"
    ]

    for keyword in required_keywords:
        assert keyword.lower() in content.lower(), f"DEPLOYMENT.md should mention {keyword}"


def test_vercel_cli_check():
    """Test that Vercel CLI availability is documented (not necessarily installed)."""
    project_root = Path(__file__).parent.parent
    deployment_md_path = project_root / "DEPLOYMENT.md"

    with open(deployment_md_path, 'r') as f:
        content = f.read()

    # Should mention Vercel CLI
    assert "vercel" in content.lower(), "DEPLOYMENT.md should mention Vercel CLI"


def test_architectural_limitations_documented():
    """Test that architectural limitations are documented."""
    project_root = Path(__file__).parent.parent
    deployment_md_path = project_root / "DEPLOYMENT.md"

    with open(deployment_md_path, 'r') as f:
        content = f.read()

    # Should mention Streamlit or architectural considerations
    has_streamling_note = "streamlit" in content.lower()
    has_architecture_note = "architecture" in content.lower() or "limitation" in content.lower()

    assert has_streamling_note or has_architecture_note, \
        "DEPLOYMENT.md should document architectural considerations or limitations"


def test_alternative_deployments_documented():
    """Test that alternative deployment options are mentioned."""
    project_root = Path(__file__).parent.parent
    deployment_md_path = project_root / "DEPLOYMENT.md"

    with open(deployment_md_path, 'r') as f:
        content = f.read()

    # Should mention alternatives
    alternatives = ["streamlit cloud", "railway", "render", "fly.io", "alternative"]
    has_alternative = any(alt in content.lower() for alt in alternatives)

    assert has_alternative, "DEPLOYMENT.md should mention alternative deployment options"
