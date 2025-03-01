#!/bin/bash

# Create a test file if it doesn't exist
TEST_FILE="test_file.txt"
echo "This is a test file for the streaming file server." > "$TEST_FILE"

echo "Uploading file to server..."
curl -v -X POST -F "file=@$TEST_FILE" http://localhost:8080/api/files/upload

echo -e "\n\nDone!"
