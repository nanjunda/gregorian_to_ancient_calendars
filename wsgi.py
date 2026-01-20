import sys
import os

# Ensure the application directory is in the path
# Standard for mod_wsgi and other production servers
sys.path.insert(0, os.path.dirname(__file__))

# Import the WSGI application from the gateway
# gateway:application is the DispatcherMiddleware wrapping all modules
from gateway import application

if __name__ == "__main__":
    # If run directly, behave like gateway.py
    from werkzeug.serving import run_simple
    print("🚀 Running Ancient Calendars v2.0 WSGI Bridge...")
    run_simple('0.0.0.0', 5080, application, use_reloader=True, use_debugger=True)
