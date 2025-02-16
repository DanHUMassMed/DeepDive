#!/bin/bash
curl -X 'POST'   'http://127.0.0.1:8000/chat/'   -H 'Content-Type: application/json'   -d '{
  "prompt": "Hello, how are you?"
}'