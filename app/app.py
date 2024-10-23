import logging

import threading
import os
import sys

from flask import Flask, request, jsonify, Response,send_from_directory
from flask_cors import CORS

import jsonschema
from jsonschema import validate
from jsonschema.exceptions import ValidationError

# -- local imports
from app.config import config
from app.utils import get_ip, get_process_metrics
from app.sse.routes import setup_sse_listen, notify_subscribers, stream
from app.schema import likert_schema, user_schema, answer_schema


# ---------------------------------------------------------------------------------------------------- Global vars
version = "0.1.0"
nicknames = {}
likertScores = {}
#static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../static'))
static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../docs'))


# ---------------------------------------------------------------------------------------------------- Setup logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    print("no logger handlers")
print(f"static_folder: {static_folder}")
# ---------------------------------------------------------------------------------------------------- Helper functions
# Check if the static_folder exists
if not os.path.exists(static_folder):
      logger.warning(f"Directory does not exist: {static_folder}")
#     static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../static'))

# ---------------------------------------------------------------------------------------------------- Flask app
app = Flask(__name__)
# ---------------------------------------------------------------------------------------------------- Flask CORS
# CORS is done with Nginx

# ---------------------------------------------------------------------------------------------------- SSE setup

sse_manager = setup_sse_listen(app, config.sse_port) # Setup SSE listening route


# ---------------------------------------------------------------------------------------------------- Event routes
# test with
# curl -X GET http://localhost:5050/health
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for the SSE server."""
    return jsonify({"status": "healthy","version": version}), 200

# test with
# curl -X GET http://localhost:5050/events
@app.route('/events')
def events():
    """starts SSE endpoint for both pings and name changes."""
    return Response(stream(sse_manager), mimetype='text/event-stream')

# test with
# curl -X GET http://localhost:5050/ping
# ping is disabled
@app.route('/ping', methods=['GET'])
def ping():
    """Endpoint to simulate a ping event."""
    notify_subscribers(sse_manager,"Pinged", "PING")  # Notify subscribers of the ping event
    return "Pinged\n"

# ---------------------------------------------------------------------------------------------------- Nickname routes

# post a nickname identified by user and user id
# curl -X POST -H "Content-Type: application/json" -d '{"user":"Hund", "uuid":"123"}' http://localhost:5050/nickname
@app.route('/nickname', methods=['POST'])
def post_icon_name():
    """Receive a JSON object with a name field, which is equivalent to a anonymous login."""
    data = request.get_json()  # Extract JSON data from request
    try:
        validate(data, user_schema)
    except ValidationError as e:
        logger.error(f"Validation error: {e.message}")
        logger.error(f"Checked against schema: {likert_schema}")
        return jsonify({'status': 'error', 'message': 'Validation error'}), 400
    uuid = data['uuid']
    nicknames[uuid] = data['user']  # Store the name in the global dictionary
    logger.info(f"nicknames: {nicknames}")
    notify_subscribers(sse_manager,{"nicknames":list(nicknames.values()) }, "NICKNAME")  # Notify subscribers with the new name
    return jsonify({'status': 'success', 'message': 'Data received'}), 200

# test with
# curl -X GET http://localhost:5050/nickname/123
@app.route('/nickname/<uuid>', methods=['GET'])
def get_icon_name(uuid):
    """Return the nickname for the given uuid or None."""
    name = nicknames.get(uuid)
    if name is None:
        return jsonify({'warning': f'No name found for the given uuid: {uuid}'}), 200
    else:
        return jsonify({'nickname': name}), 200

# test with
# curl -X GET http://localhost:5050/nicknames
@app.route('/nicknames', methods=['GET'])
def get_icon_names():
    """Return the list of nicknames."""
    return jsonify({'nicknames': list(nicknames.values())}), 200

# ----------------------------------------------------------------------------------------------------- Likert scale routes
# test with
# curl -X POST -H "Content-Type: application/json" -d '{"likert":"scale1", "user":"Hund", "value":"3" }' http://localhost:5050/likert
@app.route('/likert', methods=['POST'])
def post_likert():
    """Receive a JSON object with a likert field."""
    data = request.get_json()
    logger.info(f"Received data: {data}")
    # check against json schema
    try:
        validate(data, likert_schema)
    except ValidationError as e:
        logger.error(f"Validation error: {e.message}")
        logger.error(f"Checked against schema: {likert_schema}")
        return jsonify({'status': 'error', 'message': 'Validation error'}), 400
    # copy field likert and value to a new dictionary
    # update = {'likert': data['likert'], 'value': data['value']}
    user = data['user']
    # check if the user is known
    logger.info(f"nicknames: {nicknames}")
    if user not in nicknames.values():
        return jsonify({'status': 'error', 'message': 'Unknown user can not vote'}), 400
    # create or update a nested dictionary with user and likert as keys
    likertScores.setdefault(data['likert'], {})[user] = data['value']
    notify_subscribers(sse_manager, {"percentage": calcLikertPercentage(likertScores[data['likert']])} , f'A-{data["likert"]}')  # Notify subscribers with the new name
    return jsonify({'status': 'success', 'message': f'Data received for key {data["likert"]}'}), 200

# test with
@app.route('/likerts', methods=['GET'])
# curl -X GET http://localhost:5050/likerts
def get_likert():
    """Return the list of likert scores."""
    logger.warning("likertScores: {likertScores}")
    return jsonify({'likert': likertScores}), 200

# get the likert score for all users and ONE likert id in percentage with 0:100%, 1:75%, 2:50%, 3:25%, 4:0%
@app.route('/likert/<likert_id>', methods=['GET'])
# curl -X GET http://localhost:5050/likert/scale1
def get_likert_scale(likert_id):
    # contribution = {"0":1, "1":0.75, "2":0.5, "3":0.25, "4":0}
    """Return the list of likert scores for a specific likert id."""
    if likert_id not in likertScores:
        return jsonify({'warning': f'No likert scores found for the given likert id: {likert_id}'}), 200
    else:
        return jsonify({'likert': calcLikertPercentage(likertScores[likert_id])}), 200
        # percentage = 100 - (scores[likert_id] * 25)
        # return jsonify({'likert': percentage}), 200


def calcLikertPercentage(likertScores):
    contribution = {"0":1, "1":0.75, "2":0.5, "3":0.25, "4":0}
    # calculate the percentage of the likert score
    scores = likertScores
    contribs = [contribution[score] for score in list(scores.values())]
    # average the contributions
    percentage = sum(contribs) / len(contribs) * 100
    return round(percentage)
# ------------------------------------------------------------------------------------------------------ Answer routes
answers = {}
# post an answer identified by user and question id
# curl -X POST -H "Content-Type: application/json" -d '{"answer":"I mean yes", "qid":"inputField1", "user":"Hund"}' http://localhost:5050/answer
@app.route('/answer', methods=['POST'])
def post_answer():
    """Receive a JSON object with a answer field."""
    data = request.get_json()
    try:
        validate(data, answer_schema)
    except ValidationError as e:
        logger.error(f"Validation error: {e.message}")
        logger.error(f"Checked against schema: {likert_schema}")
        return jsonify({'status': 'error', 'message': 'Validation error'}), 400
    # check if the uuid is known
    user = data['user']
    qid = data['qid']
    if user not in nicknames.values():
        logger.error(f"Unknown user: {user}")
        return jsonify({'status': 'error', 'message': 'Unknown uuid'}), 400
    # store the answer in a dictionary with the uuid as key, create if not exists
    d = answers.setdefault(qid, {})
    d[user] = data['answer']
    # notify the subscribers
    logger.info("nicknames:", nicknames)
    logger.info("answers:", answers)
    notify_subscribers(sse_manager, {"qid":qid,"answers": list(answers[qid].values())}, f'A-{qid}')  # Notify subscribers with the new name
    return jsonify({'status': 'success', 'message': 'Data received'}), 200
# get all answers for a question without the uuid
# curl -X GET http://localhost:5050/answer/inputField1
@app.route('/answer/<qid>', methods=['GET'])
def get_answer(qid):
    """Return the list of answers for a question."""
    if qid not in answers:
        return jsonify({'warning': f'No answers found for the given question: {qid}'}), 200
    else:
        return jsonify({'answers': list(answers[qid].values())}), 200

# get just all answers
# curl -X GET http://localhost:5050/answers
@app.route('/answers', methods=['GET'])
def get_answers():
    """Return the list of answers for all questions."""
    return jsonify({'answers': answers}), 200


# ----------------------------------------------------------------------------------------------------- Monitoring routes
# test with
# curl -X GET http://localhost:5050/threads
@app.route('/threads')
def home():
    """Give feadback about the running threads."""
    current_thread = threading.current_thread() # Get the current thread
    message = f"Handling with: {current_thread.name}, Alive: {current_thread.is_alive()}"
    threads = threading.enumerate()  # List all live threads
    thread_info = '\n - '.join(f"{thread.name} (Alive: {thread.is_alive()})" for thread in threads)
    return f'Active threads:\n - {thread_info} \n => {message}'

# test with
# curl -X GET http://localhost:5050/monitor
@app.route('/monitor')
def monitor():
    """Get the CPU and memory usage of the SSE server process."""
    logging.info(f"monitor global pid: {app.config['global_pid']}")
    if app.config['global_pid'] is None :
        logger.error("SSE process not started")
        return jsonify({"monitor error": "SSE process not started"}), 404
    
    metrics = get_process_metrics(app.config['global_pid'])
    return jsonify(metrics)

@app.route('/counts', methods=['GET'])
def get_listener_count():
    try:
        # Access the SSE manager stored in app extensions
        sse = app.extensions["sse-manager"]
        
        # Retrieve the actual listener count by invoking the method
        listener_count_proxy = sse.get_listener_count()  # Proxy object
        
        # Use ._getvalue() on the proxy object to force the value retrieval from the server
        listener_count = listener_count_proxy._getvalue()  # Convert AutoProxy to value
        
        return jsonify({"listener_count": listener_count}), 200
    except Exception as e:
        logger.error(f"Failed to get listener count: {e}")
        return jsonify({"error": str(e)}), 500

# test with
# curl -X GET http://localhost:5050/ipsocket
@app.route('/ipsocket')
def ipsocket():
    """Get the IP address and port number of the current machine."""
    return jsonify({"ip": get_ip(), "socketNr": config.app_socketNr})

# ----------------------------------------------------------------------------------------------------- Static routes
# start in the browser with http://localhost:5050/
# to serve the frontend application
@app.route('/')
def serve_frontend():
    user_agent = request.headers.get('User-Agent')
    logger.warning(f"User-Agent: {user_agent} serves {config.app_html}")
    
    response = send_from_directory(static_folder, config.app_html) # type: ignore

    return response
    
# test with, by getting the favicon
# curl -X GET http://localhost:5050/favicon.ico
# to serve all static files (including subdirectory assets)
@app.route('/<path:filename>')
def serve_static(filename):
    logger.info(f"serve_static: {filename} from {static_folder}")
    logger.info(f"serve_static: {filename}")
    response = send_from_directory(static_folder, filename) # type: ignore
    response.headers['Cache-Control'] = 'public, max-age=31536000'
    return response


# ----------------------------------------------------------------------------------------------------- Logging
@app.before_request
def log_request_info():
    # Log method, URL, headers, and body of the request
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    logger.info(f"Request [{request.method}] {request.url} from {client_ip}")
