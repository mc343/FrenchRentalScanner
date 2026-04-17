"""
Streamlit WSGI Adapter for Vercel Serverless Deployment

This module acts as a WSGI adapter that allows Streamlit applications to run
on Vercel's serverless platform. It configures Streamlit to run in headless mode
and forwards HTTP requests to the Streamlit server.

Environment Variables:
    STREAMLIT_SERVER_HEADLESS: Set to "true" to run Streamlit without browser UI
    STREAMLIT_SERVER_PORT: Port number for Streamlit server (default: 8501)
    STREAMLIT_SERVER_ADDRESS: Host address for Streamlit server (default: 0.0.0.0)

Usage:
    This file is automatically loaded by Vercel when a request is made to the
    /api endpoint. The handler function processes the incoming request and
    forwards it to the Streamlit application.
"""

import os
from streamlit.web.server import Server as StreamlitServer


def handler(event, context):
    """
    Vercel serverless function handler for Streamlit.

    This function is called by Vercel for each HTTP request to the serverless
    endpoint. It configures the Streamlit environment and starts the server.

    Args:
        event: Lambda event object containing HTTP request details
               (path, headers, body, query parameters, etc.)
        context: Lambda context object containing runtime information
                 (request ID, memory limit, time remaining, etc.)

    Returns:
        Response from Streamlit server processed for Vercel's HTTP response format

    Environment Configuration:
        - Sets STREAMLIT_SERVER_HEADLESS to "true" for serverless operation
        - Sets STREAMLIT_SERVER_PORT to "8501" (Streamlit default)
        - Optionally sets STREAMLIT_SERVER_ADDRESS for network binding
    """
    # Configure Streamlit for Vercel serverless environment
    # Run in headless mode (no browser UI required)
    os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")

    # Set the port for Streamlit server
    # 8501 is the default Streamlit port
    os.environ.setdefault("STREAMLIT_SERVER_PORT", "8501")

    # Set the server address (bind to all interfaces for serverless)
    # This allows Vercel's routing to reach the Streamlit server
    os.environ.setdefault("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")

    # Additional environment variables for production deployment
    # Disable file watcher (not needed in serverless)
    os.environ.setdefault("STREAMLIT_SERVER_FILE_WATCHER_TYPE", "none")

    # Disable development features
    os.environ.setdefault("STREAMLIT_RUN_ON_SAVE", "false")

    # Create and run Streamlit server
    # "main.py" is the entry point for the Streamlit application
    # "." specifies the current directory as the working directory
    server = StreamlitServer("main.py", ".")

    # Start the server and return the response
    # The server will handle the request and return an HTTP response
    # compatible with Vercel's serverless function format
    return server.serve()


# For local testing and development
if __name__ == "__main__":
    # This allows the adapter to be tested locally
    # Example: python api/index.py
    print("Streamlit WSGI Adapter for Vercel")
    print("This file is intended for Vercel deployment, not local execution.")
    print("For local development, use: streamlit run main.py")
