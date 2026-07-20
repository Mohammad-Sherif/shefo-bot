"""
WSGI entry point for PythonAnywhere.
This file is referenced by PythonAnywhere's WSGI configuration.
"""
import sys
import os
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv(project_dir / ".env")

# Import the Flask app
from webapp import app as application
