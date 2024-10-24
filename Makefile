# system python interpreter. used only to create virtual environment
PY=python
BIN=.venv/bin
FIND=find


# make it work on windows too
ifeq ($(OS), Windows_NT)
    BIN=.venv/Scripts
    PY="/c/Users/Wolfgang Spahn/scoop/shims/python3"
	FIND=gfind
endif

REMOTE_PATH=~/
IMAGE=interaktiv_server
SERVER=aws-server


help:         ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e "s/\\$$//" | sed -e "s/##//"

init:		 ## setup the environment and run tests
init: 
	$(PY) -m venv .venv

install:        ## setup the environment
install: requirements.txt requirements-dev.txt
	$(BIN)/pip install --upgrade -r requirements.txt
	$(BIN)/pip install --upgrade -r requirements-dev.txt
	$(BIN)/pip install -e .
	touch .venv

.PHONY: test
test:         ## run pytest
test: .venv
	$(BIN)/pytest

.PHONY: lint
lint:         ## run flake8
lint: .venv
	$(BIN)/flake8


docker:	      ## build docker image
docker:
	$(Docker) &
	read -p "Wait until Docker is running and press enter to continue"
	docker build -t interaktiv_server . 

.PHONY: docker-clean
docker-clean: ## remove docker image
docker-clean:
	docker rmi -f interaktiv_server

docker-save:  ## save docker image
	docker save -o $(IMAGE).tar $(IMAGE)&& gzip -9 $(IMAGE).tar

docker-upload:  	 ## Upload the docs to the server
	scp -r $(IMAGE) $(SERVER):$(REMOTE_PATH)



.PHONY: static
static:	      ## pack static files
static: static/
	tar -cvf interaktiv_server_static.tar static/ && gzip -9 interaktiv_server_static.tar 

.PHONY: dev
dev:          ## runs entry point directly
dev:
	$(BIN)/python main.py

run:	      ## run docker image
run:
	docker run -p 5050:5050 interaktiv_server

clean:        ## clean up
clean:
	rm -rf interaktiv_server.egg-info
	rm -rf .pytest_cache
	rm -rf .venv
	$(FIND) . -type f -name '*~' -delete
	$(FIND) . -type f -name '*.pyc' -delete
	$(FIND) . -type d -name '__pycache__' -delete
	# delete tex2pdf dirs
	$(FIND) . -type d -name 'tex2pdf*' -exec rm -rf {} \;