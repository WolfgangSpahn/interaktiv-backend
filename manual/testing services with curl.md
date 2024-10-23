Here’s a structured documentation curl test with added explanations for each endpoint and test. 

---

# Test the Server via Curl

This documentation outlines the process of testing the server using `curl` commands. These commands demonstrate how to interact with different endpoints for login, voting, submitting answers, and handling server-sent events (SSE). Note that authentication is minimal, as anonymity is required, and each request provides a `uuid` to identify the user. For convenience, the server URL (`localhost:5050`) is replaced with an environment variable (`$SERVER_URL`).

### Setup
Set the `SERVER_URL` environment variable before running the tests:
```bash
export SERVER_URL=http://localhost:5050
```

## User Login

### Login as Hund
This command logs in the user "Hund" with `uuid` "123".
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"name":"Hund", "uuid":"123"}' $SERVER_URL/nickname
```

### Login as Katze
This command logs in the user "Katze" with `uuid` "456".
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"name":"Katze", "uuid":"456"}' $SERVER_URL/nickname
```

### Get All Nicknames
This command retrieves a list of all nicknames that have been registered.
```bash
curl -X GET $SERVER_URL/nicknames
```

## Voting

### Submit Vote for Hund
This submits a vote for user "Hund" (`uuid: 123`) on the "scale1" Likert scale with a value of 3.
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"likert":"scale1", "uid":"123", "value":"3" }' $SERVER_URL/likert
```

### Submit Vote for Katze
This submits a vote for user "Katze" (`uuid: 456`) on the "scale1" Likert scale with a value of 2.
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"likert":"scale1", "uid":"456", "value":"2" }' $SERVER_URL/likert
```

### Get All Voting Results
This retrieves the results of all voting sessions.
```bash
curl -X GET $SERVER_URL/likerts
```

### Get Results for Specific Likert Scale (scale1)
This retrieves the voting results specifically for the "scale1" Likert scale.
```bash
curl -X GET $SERVER_URL/likert/scale1
```

## Open-Ended Questions

### Submit Answer by Hund
This submits an open-ended answer "I mean yes" to question `inputField1` from user "Hund" (`uuid: 123`).
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"answer":"I mean yes", "qid":"inputField1", "uuid":"123"}' $SERVER_URL/answer
```

### Submit Answer by Katze
This submits an open-ended answer "I mean no" to question `inputField1` from user "Katze" (`uuid: 456`).
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"answer":"I mean no", "qid":"inputField1", "uuid":"456"}' $SERVER_URL/answer
```

### Get Answers for a Specific Field (inputField1)
This retrieves all answers submitted for the question `inputField1`.
```bash
curl -X GET $SERVER_URL/answer/inputField1
```

### Get All Answers for All Fields and All Users
This retrieves all submitted answers for all fields and all users.
```bash
curl -X GET $SERVER_URL/answers
```

## Thread Testing

### Test Threads
This retrieves all active threads on the server (if any).
```bash
curl -X GET $SERVER_URL/threads
```

## Server-Sent Events (SSE)

### Subscribe to SSE (Get Events)
This command subscribes to the server-sent events (SSE) stream. It allows the client to listen for real-time events sent by the server.
```bash
curl -X GET $SERVER_URL/events
```

### Send Ping Event
This sends a simple "ping" event, which the server broadcasts to all subscribed clients via SSE.
```bash
curl -X GET $SERVER_URL/ping
```

### Monitor SSE Process
This monitors the current state of the SSE process on the server.
```bash
curl -X GET $SERVER_URL/monitor
```

## Miscellaneous

### Test IP Socket
This command tests the server's response to requests sent to the `/ipsocket` endpoint.
```bash
curl -X GET $SERVER_URL/ipsocket
```

---

### Notes:
- Replace the `$SERVER_URL` with the environment variable or actual URL in production (e.g., `https://my-server-url.com`).
- For local testing, use `export SERVER_URL=http://localhost:5050` to ensure the tests run correctly.
- These `curl` commands simulate different interactions with the server, including login, voting, submitting answers, subscribing to events, and monitoring threads. There is no formal authentication beyond submitting a `uuid` in the requests.