from werkzeug.middleware.dispatcher import DispatcherMiddleware
from app import app as legacy_app

# ==============================================================================
# The Ancient Calendars Gateway (v2.1)
# ==============================================================================
# This file acts as the production entry point.
# It wraps 'app.py' (The Multi-Civilization Hub) and serves it at the root '/'.
# 
# The application logic is modularized into 'engines/', allowing app.py
# to function as a unified headless hub for all civilizations.
# ==============================================================================

application = DispatcherMiddleware(legacy_app, {
    # Future expansion slots:
    # '/mayan': mayan_app,
    # '/chinese': chinese_app
})

if __name__ == "__main__":
    from werkzeug.serving import run_simple
    print("🚀 Starting Ancient Calendars Hub v2.0 (Headless Edition)...")
    print("   Mounting Multi-Calendar Gateway at /")
    run_simple('0.0.0.0', 5080, application, use_reloader=True, use_debugger=True)
