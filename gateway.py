from werkzeug.middleware.dispatcher import DispatcherMiddleware
from app import app as legacy_app

# ==============================================================================
# The Constellation Hub (Gateway)
# ==============================================================================
# This file acts as the new entry point for the application server.
# It wraps the existing 'app.py' (Legacy Hindu Panchanga) and serves it at the root '/'.
# 
# This architecture allows us to mount NEW calendars (e.g., Mayan, Chinese) at
# separate paths (e.g., '/mayan') in the future WITHOUT modifying the existing
# stable code in 'app.py'.
# ==============================================================================

application = DispatcherMiddleware(legacy_app, {
    # Future expansion slots:
    # '/mayan': mayan_app,
    # '/chinese': chinese_app
})

if __name__ == "__main__":
    from werkzeug.serving import run_simple
    print("🚀 Starting Constellation Hub Gateway...")
    print("   Mounting Legacy App at /")
    run_simple('0.0.0.0', 5080, application, use_reloader=True, use_debugger=True)
