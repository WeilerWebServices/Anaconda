## Dockerfile for sentry
This still uses raw python.org and ubuntu commands, but should be made into conda packages.

## Getting Started

1. make build
1. make build_test  # Create the test container
1. make test    # This will start sentry and the test container
1. Wait a few minutes for sentry to actually start working.  Check the web interface. You will need to initialize a team and project.  The default user/pass is admin/admin.
1. NOT WORKING! Need to get API key first: Run the python script:  python raven_test.py
1. make clean_test   # This will kill the sentry container

#### To run just

This is not published yet.  This is the old way of launching it.
`docker run -d -name sentry -p 9000 crosbymichael/sentry`

By default it will use a sqlite database with the admin user created with the username `admin` and paswword `admin`.
