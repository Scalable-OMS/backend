VERSION=v1
DOCKERUSER=jarvisgaurav98

build:
	docker build -t oms-router-worker .

push:
	docker tag oms-router-worker $(DOCKERUSER)/oms-router-worker:$(VERSION)
	docker push $(DOCKERUSER)/oms-router-worker:$(VERSION)
	docker tag oms-router-worker $(DOCKERUSER)/oms-router-worker:latest
	docker push $(DOCKERUSER)/oms-router-worker:latest