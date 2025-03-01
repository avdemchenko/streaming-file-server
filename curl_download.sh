#!/bin/bash

# Check if a file ID was provided
if [ $# -lt 1 ]; then
  echo "Usage: $0 <file_id> [output_filename]"
  exit 1
fi

FILE_ID="$1"
OUTPUT_FILENAME="${2:-downloaded_file}"

# API endpoint
API_URL="http://localhost:8080/api/files/$FILE_ID"

echo "Downloading file with ID: $FILE_ID"

# Function to create a progress bar
function show_download_progress {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((width * current / total))
    local remaining=$((width - completed))
    
    # Format bytes to human-readable format
    local human_downloaded=$(numfmt --to=iec-i --suffix=B --format="%.2f" $current)
    local human_total=$(numfmt --to=iec-i --suffix=B --format="%.2f" $total)
    
    # Create the progress bar
    printf "\rDownload: ["
    printf "%${completed}s" | tr ' ' '='
    printf ">"
    printf "%${remaining}s" | tr ' ' ' '
    printf "] %3d%% %s/%s" $percentage "$human_downloaded" "$human_total"
}

# First, get the file size with a HEAD request
FILE_SIZE=$(curl -sI "$API_URL" | grep -i 'Content-Length' | awk '{print $2}' | tr -d '\r')

# Check if we got a file size
if [ -z "$FILE_SIZE" ]; then
    echo "Could not determine file size. Downloading without progress bar..."
    curl -o "$OUTPUT_FILENAME" "$API_URL"
    exit 0
fi

echo "File size: $(numfmt --to=iec-i --suffix=B --format="%.2f" $FILE_SIZE)"

# Download with a progress bar using curl and pv pipe
# If pv is installed, use it for a nice progress bar
if command -v pv &> /dev/null; then
    curl -s "$API_URL" | pv -s "$FILE_SIZE" > "$OUTPUT_FILENAME"
else
    # Fallback to a custom progress bar implementation using dd and curl
    bytes_read=0
    chunk_size=8192
    temp_file=$(mktemp)
    
    # Start the download in the background
    curl -s "$API_URL" > "$temp_file" &
    curl_pid=$!
    
    # Show progress while the file is downloading
    while kill -0 $curl_pid 2>/dev/null; do
        current_size=$(stat -f%z "$temp_file" 2>/dev/null || echo "0")
        show_download_progress $current_size $FILE_SIZE
        sleep 0.5
    done
    
    # Final progress update
    current_size=$(stat -f%z "$temp_file")
    show_download_progress $current_size $FILE_SIZE
    
    # Move the completed download to the destination
    mv "$temp_file" "$OUTPUT_FILENAME"
    echo -e "\nDownload complete: $OUTPUT_FILENAME"
fi

# Get file info
echo "Content-Type: $(file --mime-type -b "$OUTPUT_FILENAME")"
echo "File size: $(stat -f%z "$OUTPUT_FILENAME") bytes"
