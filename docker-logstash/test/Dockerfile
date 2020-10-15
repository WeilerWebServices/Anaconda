FROM ubuntu
MAINTAINER Bradley Kreider

RUN apt-get update
RUN apt-get install -y -q wget tar bzip2
RUN echo 'export PATH=/opt/anaconda/bin:$PATH' >> ~/.bashrc
RUN mkdir -p /opt
RUN wget --quiet http://repo.continuum.io/miniconda/Miniconda3-3.5.5-Linux-x86_64.sh
RUN /bin/bash /Miniconda3-3.5.5-Linux-x86_64.sh -b -p /opt/anaconda
RUN /opt/anaconda/bin/conda install pip ipython
RUN /opt/anaconda/bin/pip install python-logstash
RUN rm /Miniconda3-3.5.5-Linux-x86_64.sh
ADD remote_logging.py /
