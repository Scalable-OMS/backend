VERSION=v1
DOCKERUSER=jarvisgaurav98

build:
	docker build -t oms-categorizer-worker .

push:
	docker tag oms-categorizer-worker $(DOCKERUSER)/oms-categorizer-worker:$(VERSION)
	docker push $(DOCKERUSER)/oms-categorizer-worker:$(VERSION)
	docker tag oms-categorizer-worker $(DOCKERUSER)/oms-categorizer-worker:latest
	docker push $(DOCKERUSER)/oms-categorizer-worker:latest