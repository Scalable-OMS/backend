VERSION=v1
DOCKERUSER=jarvisgaurav98

build:
	docker build -t oms-notifier-worker .

push:
	docker tag oms-notifier-worker $(DOCKERUSER)/oms-notifier-worker:$(VERSION)
	docker push $(DOCKERUSER)/oms-notifier-worker:$(VERSION)
	docker tag oms-notifier-worker $(DOCKERUSER)/oms-notifier-worker:latest
	docker push $(DOCKERUSER)/oms-notifier-worker:latest