#!/bin/bash

# Start Redis server in the background
redis-server --daemonize yes

# Wait for Redis to be ready
while ! redis-cli ping; do
    sleep 1
done

# Use the AWS Lambda Python runtime interface
python -m awslambdaric letterboxdscraper.handler

