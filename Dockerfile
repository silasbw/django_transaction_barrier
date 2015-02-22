# https://docs.docker.com/articles/dockerfile_best-practices/
# Check for updates:
#   https://github.com/phusion/baseimage-docker/blob/master/Changelog.md
FROM phusion/baseimage:0.9.16

# Set correct environment variables.
ENV HOME /root

# Install dependencies.
RUN apt-get update && \
    apt-get install -y \
    libpq-dev \
    postgresql \
    python-dev \
    python-pip \
    python-virtualenv \
    python-yaml \
    rabbitmq-server

COPY testproject/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Clean up.
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY testproject/run-rabbitmq.sh /etc/service/rabbitmq/run
COPY testproject/run-celery.sh /etc/service/celery/run

COPY . /django_transaction_barrier

WORKDIR /django_transaction_barrier/testproject

RUN ./manage.py syncdb --noinput

CMD ["/sbin/my_init", "--quiet", "--", "sh", "-c", "sleep 5; ./tests.py"]
