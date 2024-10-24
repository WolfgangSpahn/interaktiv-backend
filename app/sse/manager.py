""" interaktiv
    Provides two threadsafe methods for serving Server-Sent Events (SSE) to
    multiple clients:
        - sse_put(item): adds a new item to the SSE stream
        - sse_listen(): returns a queue.Queue that blocks until a new item is
          added to the SSE stream
    Needs to be started in a separate process, like this:
	
	```
    # Starting the SSE server in a separate process

    sse_process = Process(target=start_sse, daemon=True)
    sse_process.start()
	```
"""

import logging
from multiprocessing import Lock
from multiprocessing.managers import BaseManager

from .announcer import MessageAnnouncer

from app.log_config import setup_logging

logger = logging.getLogger(__name__)

class SSEManager(BaseManager):
    pass

# start the SSE server
def start_sse(ready_event, sse_port):
	setup_logging()
	try:
		logger.info("SSE -- process: start")
		lock = Lock() # Create a mutex lock to ensure thread-safe operations.
		# create annoucer object which pings the clients
		sse = MessageAnnouncer()
		
		# listens for new SSE messages. It returns a queue.Queue that blocks until a 
        # new item is added to the SSE stream
		def sse_listen():
			with lock:
				logger.debug("SSE -- process: listen")
				message = sse.listen()
				logger.debug(f"SSE -- received: {message}")
				return message
		
		# adds a new item to the SSE stream
		def sse_put(item):
			with lock:
				logger.debug(f"SSE -- Sending SSE message: {item}")
				sse.announce(item)

		# Retrieve the number of current listeners
		def get_listener_count():
			with lock:
				# Count the number of items in listener_locks
				listener_count = len(sse.listener_locks)
				logger.debug(f"SSE -- Current listener count: {listener_count}")
				return listener_count

		# register the methods of the SSE server
		SSEManager.register("sse_listen", sse_listen)
		SSEManager.register("sse_put", sse_put)
		SSEManager.register("get_listener_count", get_listener_count)

		# start the server, to be run in a separate process
		# Define the server's address and auth key.
		manager = SSEManager(address=("127.0.0.1", sse_port), authkey=b'sse')
		
		logger.info(f"SSE -- serving SSE server at address {manager.address}")
		ready_event.set()
		server = manager.get_server()
		server.serve_forever()
	except Exception as e:
		logging.error(f"SSE Manager -- Failed to start SSE server: {e}")
	
# register the methods of the SSE server, so that they can be called from
# another process
SSEManager.register("sse_listen")
SSEManager.register("sse_put")
SSEManager.register("get_listener_count")