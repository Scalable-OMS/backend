VERSION=v1
DOCKERUSER=jarvisgaurav98

build:
	docker build -t oms-server .

push:
	docker tag oms-server $(DOCKERUSER)/oms-server:$(VERSION)
	docker push $(DOCKERUSER)/oms-server:$(VERSION)
	docker tag oms-server $(DOCKERUSER)/oms-server:latest
	docker push $(DOCKERUSER)/oms-server:latest