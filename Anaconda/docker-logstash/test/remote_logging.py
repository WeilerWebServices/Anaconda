import os 
import sys
import logging

try:
    # python 2.7 needs to use urlparse
    import urlparse as parse
except ImportError:
    # python 3 has urllib.parse
    from  urllib import parse

import logstash

def main():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


    # use for testing the script locally
    CONN = os.environ.get("LOGSTASH_PORT")
    if CONN is None:
        logger.critical("====== Couldn't find logstash container -- logging locally =========")
        logger.critical("====== If you aren't testing locally, then this is an error ========")

    # Test locally without using the Container
    CONN=("tcp://localhost:514")
    url = parse.urlsplit(CONN)

    # Docker linking sets up the ENV variable 
    #url = parse.urlsplit(os.environ.get("LOGSTASH_PORT"))

    test_logger = logging.getLogger('logstash!')
    test_logger.setLevel(logging.DEBUG)
    test_logger.addHandler(logstash.TCPLogstashHandler(url.hostname, url.port, version=1))

    # send some messages
    test_logger.critical("critial message")
    test_logger.warning("warning message1")
    test_logger.info("info message")
    test_logger.debug("debug message")

    logger.info("Check the Logstash web interface to make sure the log messages worked.")

if __name__ == "__main__":
    main()
