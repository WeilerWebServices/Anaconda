FROM ubuntu

#RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-get update

RUN apt-get install -y language-pack-en
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

RUN locale-gen en_US.UTF-8
RUN dpkg-reconfigure locales

RUN apt-get install -y \
    libxml2-dev \
    python \
    libc-dev \
    build-essential \
    make \
    gcc \
    g++ \
    python-dev \
    wget

RUN wget http://python-distribute.org/distribute_setup.py 
RUN python distribute_setup.py

RUN wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py 
RUN python get-pip.py

RUN pip install sentry

RUN apt-get install -y postgresql-client postgresql-client-common libpq5
RUN apt-get install -y libpq-dev

RUN pip install psycopg2


EXPOSE 9000

# Create a data volume that can be mounted by other containers
VOLUME ["/opt/data"]

# Copy build files to container root
RUN mkdir /app
ADD . /app

RUN mkdir -p /opt/data
ADD conf/sentry.conf.py /opt/sentry.conf.py.default
ADD conf/sentry.db /opt/data/sentry.db

# Older versions of sentry don't allow you to specify config in configure()
RUN mkdir -p /.sentry
ADD conf/sentry.conf.py.root /.sentry/sentry.conf.py

RUN /usr/bin/python /app/sentry_init.py

# Start sentry with dynamic configuration
ENTRYPOINT ["/app/bin/boot"]
