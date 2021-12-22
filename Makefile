TAG = latest
APP = $(shell basename $(CURDIR))
build:
	docker build -t registry.gitlab.exphost.pl/exphost-software/$(APP):$(TAG) .

push:
	docker push registry.gitlab.exphost.pl/exphost-software/$(APP):$(TAG)

run:
	docker run  --rm -e FLASK_ENV=development -p 5000:5000 -it registry.gitlab.exphost.pl/exphost-software/$(APP):$(TAG)

test:
	docker run  --rm -e FLASK_ENV=development -p 5000:5000 -it registry.gitlab.exphost.pl/exphost-software/$(APP):$(TAG) pytest --cov --cov-report=term --cov=report=xml

lint:
	docker run  --rm -e FLASK_ENV=development -p 5000:5000 -it registry.gitlab.exphost.pl/exphost-software/$(APP):$(TAG) flake8
