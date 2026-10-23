import os
import sys

# Make the project root importable inside Vercel's serverless function.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inventory_system.wsgi import application  # noqa: E402

app = application
