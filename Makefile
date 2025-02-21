
default:
	@echo "Call a specific subcommand:"
	@echo
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null\
	| awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}'\
	| sort\
	| egrep -v -e '^[^[:alnum:]]' -e '^$@$$'
	@echo
	@exit 1

.state/docker-build-web: Dockerfile requirements.txt requirements-dev.txt
	# Build our web container for this project.
	docker compose build --build-arg  USER_ID=$(shell id -u)  --build-arg GROUP_ID=$(shell id -g) --force-rm web

	# Mark the state so we don't rebuild this needlessly.
	mkdir -p .state
	touch .state/docker-build-web

serve: .state/docker-build-web
	docker compose up --remove-orphans -d

shell: serve
	docker compose run --rm web /bin/bash

lint: serve
	docker compose run --rm web isort --check-only .
	docker compose run --rm web black --check .

reformat: serve
	docker compose run --rm web isort .
	docker compose run --rm web black .

test: serve
	docker compose run --rm web pytest --cov=src.muse --cov-report=term-missing

check: test lint

clean:
	docker compose down -v
	rm -f .state/docker-build-web

.PHONY: default serve shell lint reformat test check clean