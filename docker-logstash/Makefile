NAME = pblittle/docker-logstash
VERSION = 0.4.0


# Set the LOGSTASH_CONFIG_URL env var to your logstash.conf file.
# We will use our basic config if the value is empty.
#LOGSTASH_CONFIG_URL ?= https://gist.github.com/pblittle/8778567/raw/logstash.conf

# This default host and port are for using the embedded elasticsearch
# in LogStash. Set the ES_HOST and ES_PORT to use a node outside of
# this container
#
ES_HOST ?= 127.0.0.1
ES_PORT ?= 9200

# The default logstash-forwarder keys are insecure. Please do not use in production.
# Set the LF_SSL_CERT_KEY_URL and LF_SSL_CERT_URL env vars to use your secure keys.
#
LF_SSL_CERT_KEY_URL ?= https://gist.github.com/pblittle/8994708/raw/insecure-logstash-forwarder.key
LF_SSL_CERT_URL ?= https://gist.github.com/pblittle/8994726/raw/insecure-logstash-forwarder.crt

DIR := ${CURDIR}

#LOGSTASH_CONFIG_FILE=$(CURDIR)/logstash.conf
LOGSTASH_CONFIG_FILE=/home/docker/logstash.conf
LOGSTASH_CONFIG_FILE_DEST=/opt/mounted/logstash.conf

# Cleanup even if not needed succeed
clean:
	docker kill logstash &>/dev/null || /usr/bin/true
	docker rm logstash &>/dev/null || /usr/bin/true
	rm -f .build_test

build:
	docker build --rm -t $(NAME):$(VERSION) .

run:
    # Needed for Boot2docker, but will fail on real Docker machine
	scp -i ~/.ssh/id_boot2docker -P 2022 logstash.conf docker@localhost:.
	docker run -d \
		-e ES_HOST=${ES_HOST} \
		-e ES_PORT=${ES_PORT} \
		-e LF_SSL_CERT_URL=${LF_SSL_CERT_URL} \
		-e LF_SSL_CERT_KEY_URL=${LF_SSL_CERT_KEY_URL} \
		-p ${ES_PORT}:${ES_PORT} \
		-p 514:514 \
		-p 9292:9292 \
		-v ${LOGSTASH_CONFIG_FILE}:${LOGSTASH_CONFIG_FILE_DEST} \
		--name logstash \
		$(NAME):$(VERSION)

tag:
	docker tag $(NAME):$(VERSION) $(NAME):latest

release:
	docker push $(NAME)

shell:
	docker run -t -i --rm $(NAME):$(VERSION) bash

build_test:
	docker build --rm -t logstash_test test
	touch .build_test

.PHONY: test
test: 
	scp -i ~/.ssh/id_boot2docker -P 2022 logstash.conf docker@localhost:.
	# Start logstash if needed -- otherwise don't bitch if it is running
	docker run -d -p 514:514 -p 9292:9292 -v ${LOGSTASH_CONFIG_FILE}:${LOGSTASH_CONFIG_FILE_DEST} --name logstash $(NAME):$(VERSION) || /usr/bin/true
	docker run -i --link logstash:logstash -v $(DIR)/test:/test -t logstash_test /bin/bash

clean_test:
	docker kill logstash
	docker rm logstash
