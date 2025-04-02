# Makefile for building and pushing Docker image

# Variables
IMAGE_NAME = wfcrai-agent-utils
TAG = latest
REGISTRY = us-central1-docker.pkg.dev/gcp-wow-food-fco-auto-dev/wfcrai-agents
FULL_IMAGE_NAME = $(REGISTRY)/$(IMAGE_NAME):$(TAG)

# Default target
.PHONY: all
all: build push

# Build the Docker image
.PHONY: build
build:
	docker build -t $(IMAGE_NAME):$(TAG) .

# Tag and push the Docker image to the registry
.PHONY: push
push:
	docker tag $(IMAGE_NAME):$(TAG) $(FULL_IMAGE_NAME)
	docker push $(FULL_IMAGE_NAME)

.PHONY: utils
utils:
	uv build
	uv pip install dist/*.whl