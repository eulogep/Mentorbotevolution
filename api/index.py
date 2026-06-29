"""
Vercel Serverless Entry Point
Forwarding requests to the main Flask application
Auteur: MABIALA EULOGE
"""

import os
import sys

# Add root folder to python path so main and src are importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Vercel requirements: the WSGI application must be exposed as 'app'
# 'app' is imported from main.py and exposed here
