NAME = bkreider/docker-sentry
VERSION = 0.1.0

# For Boot2Docker
SENTRY_CONFIG_FILE=/home/docker/sentry.conf.py
SENTRY_CONFIG_FILE_DEST=/opt/sentry.conf.py.mounted

DIR := ${CURDIR}

clean:
	docker kill sentry &>/dev/null || /usr/bin/true
	docker rm sentry &>/dev/null || /usr/bin/true
	rm -f .build_test

build:
	docker build --rm -t $(NAME):$(VERSION) .

run:
	# Needed for Boot2docker, but will fail on real Docker machine
	scp -i ~/.ssh/id_boot2docker -P 2022 sentry.conf.py docker@localhost:.
	docker run -d \
		-p 9000:9000 \
		--name sentry \
        -v ${SENTRY_CONFIG_FILE}:${SENTRY_CONFIG_FILE_DEST} \
		$(NAME):$(VERSION)

tag:
	docker tag $(NAME):$(VERSION) $(NAME):latest

release:
	docker push $(NAME)

shell:
	docker run -t -i --rm $(NAME):$(VERSION) bash

build_test:
	docker build --rm -t sentry_test tests
	touch .build_test

test:
	# Try to run -- might be running already
	docker run -d -p 9000:9000 --name sentry $(NAME):$(VERSION) || /usr/bin/true
	docker run -i --link sentry:sentry -t sentry_test /bin/bash

clean_test:
	docker kill sentry
	docker rm sentry
