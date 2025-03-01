#!/bin/bash

# Check if a file path was provided
if [ $# -lt 1 ]; then
  echo "Usage: $0 <file_path> [chunk_size_kb]"
  exit 1
fi

FILE_PATH="$1"
FILENAME=$(basename "$FILE_PATH")
FILE_SIZE=$(stat -f%z "$FILE_PATH")

# Default chunk size is 256KB unless specified
CHUNK_SIZE_KB=${2:-256}
CHUNK_SIZE=$((CHUNK_SIZE_KB * 1024))

# Generate a unique identifier
IDENTIFIER=$(uuidgen)

# Calculate number of chunks
TOTAL_CHUNKS=$(( (FILE_SIZE + CHUNK_SIZE - 1) / CHUNK_SIZE ))

echo "Uploading $FILENAME ($FILE_SIZE bytes) in $TOTAL_CHUNKS chunks"
echo "Identifier: $IDENTIFIER"

# API endpoint
API_URL="http://localhost:8080/api/files/upload/chunked"

# Progress bar function
function show_progress {
    local current=$1
    local total=$2
    local bytes_uploaded=$3
    local total_bytes=$4
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((width * current / total))
    local remaining=$((width - completed))
    
    # Format bytes to human-readable format
    local human_uploaded=$(numfmt --to=iec-i --suffix=B --format="%.2f" $bytes_uploaded)
    local human_total=$(numfmt --to=iec-i --suffix=B --format="%.2f" $total_bytes)
    
    # Create the progress bar
    printf "\rProgress: ["
    printf "%${completed}s" | tr ' ' '='
    printf ">"
    printf "%${remaining}s" | tr ' ' ' '
    printf "] %3d%% %s/%s" $percentage "$human_uploaded" "$human_total"
}

# Function to check if a chunk exists
check_chunk() {
  local chunk_number=$1
  local response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL?flowChunkNumber=$chunk_number&flowTotalChunks=$TOTAL_CHUNKS&flowChunkSize=$CHUNK_SIZE&flowTotalSize=$FILE_SIZE&flowIdentifier=$IDENTIFIER&flowFilename=$FILENAME")
  echo $response
}

# Initialize progress variables
BYTES_UPLOADED=0

# Loop through chunks and upload
for ((chunk_number=1; chunk_number<=TOTAL_CHUNKS; chunk_number++)); do
  # Calculate start position for this chunk
  start_pos=$(( (chunk_number - 1) * CHUNK_SIZE ))
  
  # Calculate end position for this chunk
  if [ $chunk_number -eq $TOTAL_CHUNKS ]; then
    # Last chunk might be smaller
    end_pos=$FILE_SIZE
  else
    end_pos=$(( chunk_number * CHUNK_SIZE ))
  fi
  
  # Calculate actual chunk size
  actual_chunk_size=$(( end_pos - start_pos ))
  
  # Check if the chunk already exists
  response=$(check_chunk $chunk_number)
  
  if [ "$response" = "200" ]; then
    echo -e "\nChunk $chunk_number already exists, skipping"
    # Update progress for skipped chunks
    BYTES_UPLOADED=$((BYTES_UPLOADED + actual_chunk_size))
    show_progress $chunk_number $TOTAL_CHUNKS $BYTES_UPLOADED $FILE_SIZE
    continue
  fi
  
  echo -e "\nUploading chunk $chunk_number/$TOTAL_CHUNKS ($actual_chunk_size bytes)"
  
  # Extract the chunk to a temporary file
  dd if="$FILE_PATH" of=temp_chunk bs=1 skip=$start_pos count=$actual_chunk_size status=none
  
  # Upload the chunk
  response=$(curl -s -o curl_response.json -w "%{http_code}" \
    -F "flowChunkNumber=$chunk_number" \
    -F "flowTotalChunks=$TOTAL_CHUNKS" \
    -F "flowChunkSize=$CHUNK_SIZE" \
    -F "flowTotalSize=$FILE_SIZE" \
    -F "flowIdentifier=$IDENTIFIER" \
    -F "flowFilename=$FILENAME" \
    -F "file=@temp_chunk" \
    "$API_URL")
  
  # Remove the temporary chunk file
  rm temp_chunk
  
  # Update progress
  BYTES_UPLOADED=$((BYTES_UPLOADED + actual_chunk_size))
  show_progress $chunk_number $TOTAL_CHUNKS $BYTES_UPLOADED $FILE_SIZE
  
  if [ "$response" = "200" ] || [ "$response" = "201" ]; then
    echo -e "\nChunk $chunk_number uploaded successfully"
    
    # Check if this is the last chunk
    if [ $chunk_number -eq $TOTAL_CHUNKS ]; then
      echo -e "\nAll chunks uploaded successfully!"
      cat curl_response.json
    fi
  else
    echo -e "\nChunk $chunk_number upload failed with code $response"
    cat curl_response.json
    exit 1
  fi
done

rm -f curl_response.json
echo -e "\nUpload complete"
