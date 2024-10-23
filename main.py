import os
import logging

# --- imports
from multiprocessing import Process, Manager, Event
from waitress import serve
from flask import g

# -- local imports
from app.app import app
from app.sse.manager import start_sse
from app.utils import get_ip
from app.log_config import setup_logging, debug_logging

# --- run main
if __name__ == '__main__':
    from app.config import config
    setup_logging()

    # --- multiprocessing -- Shared dictionary for managing data between processes
    # Store shared_data in Flask global context

    # --- start the SSE server
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
        logging.info(f"serve in LAN http://{get_ip()}:{config.app_socketNr}")
        # process event to synchronize server startups, wait for SSE server to be ready
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            logging.info("We run under Werkzeug, so we are in the reloaded subprocess")
        elif not app.debug:
            logging.info("We run in production mode")
        sse_ready_event = Event()
        sse_process = Process(target=start_sse, daemon=True, args=(sse_ready_event,config.sse_port))
        sse_process.start()
            # Store PID in the global variable
        app.config['global_pid'] = sse_process.pid
        logging.info(f"SSE -- Started SSE server process with PID: {app.config['global_pid']}")
        sse_ready_event.wait() # wait for the server to be ready
        logging.info("Starting Flask app")
    # Start the Flask application in a separate thread
    if os.environ.get("FLASK_ENV") == "development":
        logging.info(f"Flask app running in development mode on http://{get_ip()}:{config.app_socketNr}")
        app.run(host='0.0.0.0', port=config.app_socketNr, threaded=True, debug=True)
    else:
        from waitress import serve
        logging.info(f"Serving with Waitress on http://{get_ip()}:{config.app_socketNr}")
        serve(app, host='0.0.0.0', port=config.app_socketNr, threads=100, connection_limit=100)