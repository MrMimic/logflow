#!/usr/bin/bash

# This bash client will call the train.py script inside logflow Docker.
# It will launch the real training and store the model.

# Get data path from arguments
DATA_PATH=$1
if [ ! -d "$DATA_PATH" ]; then
    echo "Please provide an existing data folder ($DATA_PATH)."
    exit 1
fi

API_PATH="$PWD/api"
if [ ! -d "$API_PATH" ]; then
    echo "Please run this script from the cloned repository with:"
    echo "    bash scripts/train.sh"
    exit 1
fi

# Create a persistent folder to save the model
OUTPUT_DIRECTORY=$PWD/model
if [ ! -d "$OUTPUT_DIRECTORY" ]; then
    mkdir "$OUTPUT_DIRECTORY"
fi

# Launch the docker with mounted volumes
DOCKER_ID=$(docker run \
    -it -d \
    --pid=host \
    --name LOGFLOW \
    -v "$API_PATH":/home/api \
    -v "$DATA_PATH":/home/data \
    -v "$PWD":/home/code \
    -v "$OUTPUT_DIRECTORY":/home/output \
    logflow /bin/bash)

# Train the model and save it under OUTPUT_DIRECTORY
docker exec LOGFLOW bash -c "python3 /home/api/scripts/train.py"

# Remove the useless docker
docker stop "$DOCKER_ID" > /dev/null
docker rm "$DOCKER_ID" > /dev/null
