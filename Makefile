# ===================================================================================================
# Makefile for building and killing services in the Fire Detection And Monitoring Platform
# _PORT variables should have the same values as Port number specified in service's Dockerfile
# Set Absolute Paths for DATASET_PATH and DOCKER_COMPOSE_PATH according to the setup on your machine
# ===================================================================================================

# Jupyter Variables
JUPYTER_IMAGE_NAME = mainproject/anomaly-platform-jupyter
JUPYTER_DOCKERFILE = jupyter/Dockerfile
JUPYTER_TOKEN = dummytoken
JUPYTER_PORT = 8888

# set DATASET_PATH to absolute path of directory where train.csv and test.csv are present
DATASET_PATH = F:/projects/detection-monitoring-platform/jupyter

# set absolute path of directory where docker-compose.yml file is located
DOCKER_COMPOSE_PATH = F:/projects/detection-monitoring-platform/monitoring

# Prediction API Variables
API_IMAGE_NAME = mainproject/anomaly-platform-api
API_DOCKERFILE = service/Dockerfile
# Same as port in uvicorn.run() in main.py
API_PORT = 8000

# Python Virtual Environment Variables
# Windows is the default OS. Specify OS=<YOUR_OS_NAME> along with the 'make' command if you're running a different OS
OS = Windows
BIN = bin

ifeq ($(OS), Windows)
BIN = Scripts
endif

VENV = venv
PYTHON = $(VENV)/$(BIN)/python
PIP = $(VENV)/$(BIN)/pip3

.PHONY: help run-jupyter build-api run-api run-platform run-all stop-jupyter stop-api stop-platform stop-all remove-all test-platform remove-env

# Execute "run-platform" as the default target for the "make" command
.DEFAULT_GOAL := run-platform

help:	## Lists all targets in this Makefile along with their descriptions
	@echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	@echo +'                                                                        '+
	@echo +'              'Targets available for this Makefile'                       '+
	@echo +'                                                                        '+
	@echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

run-jupyter:	## Build and Run a Jupyter Lab Container
	docker build -t $(JUPYTER_IMAGE_NAME) --file $(JUPYTER_DOCKERFILE) .
	docker run -d -p $(JUPYTER_PORT):$(JUPYTER_PORT) -e JUPYTER_TOKEN=$(JUPYTER_TOKEN) --mount type=bind,source=$(DATASET_PATH),target=/src/ $(JUPYTER_IMAGE_NAME)
	@echo -------------------------------------------
	@echo Jupyter Lab URL: http://localhost:$(JUPYTER_PORT)/
	@echo Jupyter Lab Token: $(JUPYTER_TOKEN)
	
build-api:	## Build the Prediction API Docker Image
	docker build -t $(API_IMAGE_NAME) --file $(API_DOCKERFILE) .

run-api: build-api		## Build and Run a Prediction API Container
	docker run -d -p $(API_PORT):$(API_PORT) $(API_IMAGE_NAME)
	@echo -------------------------------------------
	@echo Prediction API Endpoint: http://localhost:$(API_PORT)/

run-platform: build-api	## Build and Run the entire Platform
	docker-compose -f $(DOCKER_COMPOSE_PATH)/docker-compose.yml up -d
	@echo ===========================================
	@echo Access Services Here
	@echo ===========================================
	@echo Prediction API Endpoint: http://localhost:$(API_PORT)/
	@echo Prometheus Console: http://localhost:9090/graph 
	@echo Grafana UI: http://localhost:3000/?orgId=1

run-all: run-jupyter run-platform	## Run all containers
	@echo ===========================================
	@echo Access Services Here
	@echo ===========================================
	@echo Jupyter Lab URL: http://localhost:$(JUPYTER_PORT)/
	@echo Jupyter Lab Token: $(JUPYTER_TOKEN)
	@echo Prediction API Endpoint: http://localhost:$(API_PORT)/
	@echo Prometheus Console: http://localhost:9090/graph 
	@echo Grafana UI: http://localhost:3000/?orgId=1

stop-jupyter: 	## Kill and Delete the Jupyter Lab Container
	docker stop $$(docker ps -q --filter ancestor=$(JUPYTER_IMAGE_NAME))
	@echo Stopped Jupyter Lab Container
	docker rm $$(docker ps -a -q --filter "ancestor=$(JUPYTER_IMAGE_NAME)")
	@echo Deleted Jupyter Lab Container

stop-api: 		## Kill and Delete the Prediction API Container
	docker stop $$(docker ps -q --filter ancestor=$(API_IMAGE_NAME))
	@echo Stopped Prediction API Container
	docker rm $$(docker ps -a -q --filter "ancestor=$(API_IMAGE_NAME)")
	@echo Deleted Prediction API Container

stop-platform:	# Kill and Delete the Entire Platform
	docker-compose -f $(DOCKER_COMPOSE_PATH)/docker-compose.yml stop
	@echo Stopped Anomaly Detection Platform

stop-all: stop-jupyter stop-platform 	## Kill and Delete all containers
	@echo ========== All Containers Killed ==========

remove-all:  ## Remove all Docker images
	docker rmi -f $(JUPYTER_IMAGE_NAME):latest
	docker rmi -f $(API_IMAGE_NAME):latest
	docker rmi -f prom/prometheus:v2.20.0
	docker rmi -f grafana/grafana:7.1.1
	docker rmi -f stefanprodan/caddy
	@echo ========== All Images Removed ==========

$(VENV)/$(BIN)/activate: ./tester/requirements.txt
	python -m venv $(VENV)
	$(PIP) install -r ./tester/requirements.txt

$(VENV)/$(BIN)/activate: ./detection/requirements.txt
	python -m venv $(VENV)
	$(PIP) install -r ./detection/requirements.txt

test-platform: $(VENV)/$(BIN)/activate	## Create a Python Virtual Environment, run tester.py and visualize output in Grafana
	$(PYTHON) ./tester/tester.py

run-detection: $(VENV)/$(BIN)/activate	## Create a Python Virtual Environment, run detection.py and visualize output in Grafana
	$(PYTHON) ./detection/detection.py


remove-env:	## Remove the Python Virtual Environment created for testing
	rm -rf __pycache__
	rm -rf $(VENV)