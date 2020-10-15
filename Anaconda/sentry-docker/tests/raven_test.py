import os
from raven import Client

host = os.environ.get("SENTRY_PORT_9000_TCP_ADDR", "sentry")
port = os.environ.get("SENTRY_PORT_9000_TCP_PORT", "9000")

# http://3c7352301c0f4d4390435a199cdfc2e6:eea88147a39a4c4ba7490d71edcc9a72@SENTRY_HOST:SENTRY_PORT/2
dsn = open("dsn.txt", 'r').read().strip()
secret = dsn[7:].split('@')[0]
real_dsn = "http://%s@%s:%s/2" % (secret, host, port)
client = Client(real_dsn)

try:
    1 / 0
except ZeroDivisionError:
    client.captureException()

client.captureMessage('My event just happened!')
