"""Test Streamlit WSGI adapter for Vercel deployment."""

import os
import pytest


# Get the directory of this test file
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the project root (parent of tests directory)
PROJECT_ROOT = os.path.dirname(TEST_DIR)
# Path to api/index.py
API_INDEX_PATH = os.path.join(PROJECT_ROOT, "api", "index.py")


def test_api_index_file_exists():
    """Test that api/index.py file exists."""
    assert os.path.exists(API_INDEX_PATH), f"api/index.py file should exist at {API_INDEX_PATH}"


def test_api_index_handler_exists():
    """Test that handler function exists in api/index.py."""

    with open(API_INDEX_PATH, 'r') as f:
        content = f.read()

    # Check that handler function is defined
    assert 'def handler(' in content, "handler function should be defined"
    assert 'event' in content, "handler should have event parameter"
    assert 'context' in content, "handler should have context parameter"


def test_api_index_environment_variables():
    """Test that required environment variables are set."""

    with open(API_INDEX_PATH, 'r') as f:
        content = f.read()

    # Check for Streamlit environment variable configuration
    assert 'STREAMLIT_SERVER_HEADLESS' in content, "Should set STREAMLIT_SERVER_HEADLESS"
    assert 'STREAMLIT_SERVER_PORT' in content, "Should set STREAMLIT_SERVER_PORT"


def test_api_index_streamlit_server():
    """Test that StreamlitServer is imported and created."""

    with open(API_INDEX_PATH, 'r') as f:
        content = f.read()

    # Check for StreamlitServer import and usage
    assert 'StreamlitServer' in content, "Should import or use StreamlitServer"
    assert 'StreamlitServer(' in content, "Should create StreamlitServer instance"


def test_api_index_has_documentation():
    """Test that the file has documentation comments."""

    with open(API_INDEX_PATH, 'r') as f:
        content = f.read()

    # Check for docstrings or comments
    assert '"""' in content or "'''" in content or '#' in content, "Should have documentation"
