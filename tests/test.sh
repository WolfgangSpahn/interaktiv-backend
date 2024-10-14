#!/bin/bash

# bash script test the server via curl

URL="http://localhost:5050"
# URL="https://sebayt.ch/interaktiv"

### login as Hund
curl -X POST -H "Content-Type: application/json" -d '{"user":"Hund", "uuid":"123"}' "$URL/nickname"
# as Katze
curl -X POST -H "Content-Type: application/json" -d '{"user":"Katze", "uuid":"456"}' "$URL/nickname"
# get all nicknames
curl -X GET "$URL/nicknames"

### voting
curl -X POST -H "Content-Type: application/json" -d '{"likert":"scale1", "user":"Hund", "value":"3"}' "$URL/likert"

# vote as Katze
curl -X POST -H "Content-Type: application/json" -d '{"likert":"scale1", "user":"Katze", "value":"2"}' "$URL/likert"
# get all results
curl -X GET "$URL/likerts"
# get results for scale1
curl -X GET "$URL/likert/scale1"

### answer to open-ended question
curl -X POST -H "Content-Type: application/json" -d '{"answer":"I mean yes", "qid":"inputField1", "user":"Hund"}' "$URL/answer"
curl -X POST -H "Content-Type: application/json" -d '{"answer":"I mean no", "qid":"inputField1", "user":"Katze"}' "$URL/answer"
# get answers for inputField1
curl -X GET "$URL/answer/inputField1"
# get all answers for all fields and all users
curl -X GET "$URL/answers"

### test threads
curl -X GET "$URL/threads"

### test SSE
# subscribe to SSE, request to get events
start bash -c "curl -X GET '$URL/events'; exec bash" && sleep 5

# send ping event
curl -X GET "$URL/ping"

# monitor SSE process
curl -X GET "$URL/monitor"

### test IPSocket
curl -X GET "$URL/ipsocket"
