""" 
    Configuration file for the backend. Contains all the parameters that can be changed by the user.
"""

import os
import logging
import dotenv

# Load environment variables from "../.env" file
dotenv.load_dotenv()
# load PRESENTATION_NAME from .env file
PRESENTATION_NAME = os.getenv("PRESENTATION_NAME")

logger = logging.getLogger(__name__)

logger.info(f"name for presentation in .env file: '{PRESENTATION_NAME}'")

# config.py

class Config:
    def __init__(self):
        # app
        self.app_html = PRESENTATION_NAME+".html" if PRESENTATION_NAME else "index.html"
        self.app_socketNr = 5050
        # sse demaon
        self.sse_port = 2437
        self.sse_ping = False

# Singleton instance of the Config class
config = Config()