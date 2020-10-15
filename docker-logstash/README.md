# Continuum Updates

The Makefile has tests and the default configuration file only does remote syslog on port 514 (no /var/log/* or stdin).

## Getting Started 

1. make build
1. make build_test  # Create the test container
1. make test    # This will start logstash and the test container
1. Wait a few minutes for logstash to actually start working.  Check the web interface until you can see 0 messages.  Elastic search takes a while to initializae and run even if the UI is working.
1. Run the python script:  python remote_logging.py
1. Check web interface for log messages: http://localhost:9292 or Boot2Docker:  http://192.168.59.103:9292/index.html#/dashboard/file/guided.json
1. make clean_test   # This will kill the logstash container



# Upstream Comments below


This is a logstash (1.4.2) image that is configurable to run using either the embedded elasticsearch or an elasticsearch node running in a separate container.

To fetch and start a container running logstash (1.4.2), elasticsearch (1.1.1) and Kibana 3 (3.0.1), simply:

	docker run -d \
	  --name logstash \
	  -p 514:514 \
	  -p 9200:9200 \
	  -p 9292:9292 \
	  pblittle/docker-logstash

If you want to link to an external elasticsearch container rather than the embedded server, add a link flag with your existing elasticsearch container's name. For example, to link to a container named `elasticsearch`:

	docker run -d \
	  --name logstash \
	  -link elasticsearch:es \
	  -p 514:514 \
	  -p 9292:9292 \
	  pblittle/docker-logstash

In addition to the link, if you want your elasticsearch node's `bind_host` and `port` automatically detected, you will need to set `ES_HOST` and `ES_PORT` placeholders in your `elasticsearch` definition in your logstash config file.

	output {
	  stdout {
	    codec => rubydebug
	    debug => true
	    debug_format => "json"
	  }

	  elasticsearch {
	    bind_host => "ES_HOST"
	    port => "ES_PORT"
	  }
	}

Alternatively, you can replace the placeholder values with the real elasticsearch `bind_host` and `port` values.

Without any configuration changes, an example `logstash.conf` will be created for you. You can override the example config by passing a `LOGSTASH_CONFIG_URL` env var in your `docker run` command using a `-e` flag pointing to your config file.

    docker run -d \
      --name logstash \
	  -p 514:514 \
	  -p 9292:9292 \
	  -e LOGSTASH_CONFIG_URL=https://gist.github.com/pblittle/8778567/raw/logstash.conf \
	  pblittle/docker-logstash

To build the image locally using Vagrant, perform the following steps from the project root:

    vagrant up
    vagrant ssh
    cd /vagrant

From there, to build and create a running container from the newly created image:

    make build
    make run

Special shoutout to ehazlett's excellent post, [Logstash and Kibana3 via Docker][1], explaining the big picture.

  [1]: http://ehazlett.github.io/applications/2013/08/28/logstash-kibana/
