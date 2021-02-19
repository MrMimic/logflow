#!/usr/bin/bash

# This bash client will call load the trained model.
# Then, it will launch a REST FastAPI that will expose the get_template() method.

API_PATH="$PWD"/api
OUTPUT_DIRECTORY="$PWD"/model

DOCKER_ID=$(docker run \
    -it -d \
    --pid=host \
    --name LOGFLOW \
    -p 80:80 \
    -v "$API_PATH":/home/api \
    -v "$PWD":/home/code \
    -v "$OUTPUT_DIRECTORY":/home/output \
    logflow:api /bin/bash)

# POURQUOI ENCORE BESOIN DU PIP INSTALL ? LOGIQUEMENT DANS DOCKERFILE !
docker exec LOGFLOW bash -c "python3 /home/api/scripts/serve.py"


# Remove the useless docker
docker stop "$DOCKER_ID" > /dev/null
docker rm "$DOCKER_ID" > /dev/null
