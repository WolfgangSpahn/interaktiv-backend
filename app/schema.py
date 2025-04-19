# Define your schema
likert_schema = {
    "type": "object",
    "properties": {
        "likert": {"type": "string"},
        "user": {"type": "string"},
        "value": {"type": "string", "pattern": "^[0-4]$"}  # Expecting a value from 1 to 5 in string form
    },
    "required": ["likert", "user", "value"]
}

user_schema = {
    "type": "object",
    "properties": {
        "user": {"type": "string"},
        "uuid": {"type": "string", "pattern": "^[0-9a-fA-F\\-]+$"}  # Expecting a UUID-like string
    },
    "required": ["user", "uuid"]
}

answer_schema = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},  # The "answer" must be a string
        "qid": {"type": "string"},     # The "qid" must be a string (can be an input field ID)
        "user": {"type": "string"}     # The "user" must be a string
    },
    "required": ["answer", "qid", "user"]  # All three fields are required
}
