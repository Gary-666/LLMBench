#!/usr/bin/env python3
"""
AIMS For Every API - A conversation testing framework for multiple AI APIs.
"""
import os
from dotenv import load_dotenv

from aims.cli import main

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    main()
